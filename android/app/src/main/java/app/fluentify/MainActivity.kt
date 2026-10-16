package app.fluentify

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognitionService
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.webkit.WebViewAssetLoader
import java.util.Locale

/**
 * Fluentify runs fully offline: the whole UI and the chatbot engine live in
 * assets/www. The asset loader exposes them over
 * https://appassets.androidplatform.net/ so that fetch("data/memory.json") is
 * same-origin and is not blocked by the stricter file:// origin rules.
 *
 * Speech out: the 🎧 Listening panel speaks through Android's built-in
 * text-to-speech engine via the AndroidTTS bridge (fully offline, no network,
 * no API key); on the web build the page falls back to the Web Speech API.
 *
 * Speech in: the 🎙 composer button goes the other way through the AndroidSTT
 * bridge, using RecognizerIntent - the recogniser that already ships with the
 * OS. That means no speech model to download, no API key, and nothing of the
 * learner's voice leaves the device unless they themselves enabled an online
 * recogniser in system settings (EXTRA_PREFER_OFFLINE is honoured when the
 * app is configured that way). Partial results stream back so the interim
 * text appears as they speak.
 */
class MainActivity : AppCompatActivity() {

    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var web: WebView? = null

    /* Callbacks handed to the STT bridge for this one recognition. */
    private var sttPartial: ((String) -> Unit)? = null
    private var sttFinal: ((String) -> Unit)? = null
    private var sttError: ((String) -> Unit)? = null

    private val micPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                startRecognizer(sttLanguage)
            } else {
                sttError?.invoke("not-allowed")
                clearSttCallbacks()
            }
        }

    private val recognizerLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            // result.data is an Intent?, and mixing it with a Bundle fallback
            // widens the expression to their common supertype - so the Intent
            // methods below stop resolving. Keep the nullable Intent and let
            // the safe call do the work.
            val results = if (result.resultCode == Activity.RESULT_OK) {
                result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            } else {
                null
            }
            val text = results?.joinToString(" ")?.trim().orEmpty()

            if (result.resultCode == Activity.RESULT_OK) {
                if (text.isNotEmpty()) {
                    sttFinal?.invoke(text)
                } else {
                    // RESULT_OK with nothing in it happens when the recogniser
                    // returns without a usable hypothesis. Saying so beats
                    // pretending the microphone is simply not responding.
                    sttError?.invoke("no-speech")
                }
            } else {
                sttError?.invoke("no-speech")
            }
            clearSttCallbacks()
        }

    private var sttLanguage: String = "en-GB"

    private fun clearSttCallbacks() {
        sttPartial = null
        sttFinal = null
        sttError = null
    }

    /**
     * A real SpeechRecognizer, not RecognizerIntent.
     *
     * RecognizerIntent launches the system dialog as its own activity: the
     * app has no handle on it, cannot stop it, gets one final answer when it
     * closes, and the page's mic button has no relationship to its lifecycle.
     * That is why holding the button left dictation running with nothing to
     * stop it, and why nothing was heard until the dialog ended.
     *
     * SpeechRecognizer is driven in-process: partial results arrive as the
     * user speaks, and stop() is immediate. On-device is preferred where the
     * system offers it, so an offline install does not stream the microphone
     * to a server - which on a phone abroad is the difference between
     * dictating and failing.
     */
    private var speech: SpeechRecognizer? = null

    private fun buildRecognizer(language: String): SpeechRecognizer? {
        val onDevice = if (android.os.Build.VERSION.SDK_INT >= 31) {
            try {
                SpeechRecognizer.isOnDeviceRecognitionAvailable(this)
            } catch (e: Exception) {
                false
            }
        } else {
            false
        }
        val made = try {
            if (onDevice) SpeechRecognizer.createOnDeviceSpeechRecognizer(this)
            else SpeechRecognizer.createSpeechRecognizer(this)
        } catch (e: Exception) {
            null
        }
        if (made == null) return null
        made.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onEvent(eventType: Int, params: Bundle?) {}

            override fun onError(error: Int) {
                // Map the platform codes onto what the page already knows how
                // to say. A bare "aborted" for everything told the user nothing.
                val code = when (error) {
                    SpeechRecognizer.ERROR_NO_MATCH,
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "no-speech"
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "network"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "not-allowed"
                    SpeechRecognizer.ERROR_AUDIO -> "audio-capture"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "busy"
                    else -> "aborted"
                }
                releaseRecognizer()
                sttError?.invoke(code)
                clearSttCallbacks()
            }

            override fun onResults(results: Bundle?) {
                val text = results
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull().orEmpty()
                releaseRecognizer()
                if (text.isBlank()) {
                    sttError?.invoke("no-speech")
                } else {
                    sttFinal?.invoke(text)
                }
                clearSttCallbacks()
            }

            override fun onPartialResults(partialResults: Bundle?) {
                // The real-time part: this fires repeatedly while they speak.
                val text = partialResults
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                if (!text.isNullOrBlank()) sttPartial?.invoke(text)
            }
        })
        sttLanguage = language
        return made
    }

    private fun startRecognizer(language: String) {
        releaseRecognizer()
        val rec = buildRecognizer(language)
        if (rec == null) {
            // No in-process recogniser: fall back to the system dialog, which
            // at least transcribes something on a device that offers nothing
            // better.
            launchRecognizerDialog(language)
            return
        }
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        speech = rec
        try {
            rec.startListening(intent)
        } catch (e: Exception) {
            releaseRecognizer()
            sttError?.invoke("service-not-allowed")
            clearSttCallbacks()
        }
    }

    /** stopListening gives the engine a chance to emit what it heard. */
    private fun stopRecognizer() {
        val rec = speech ?: return
        try {
            rec.stopListening()
        } catch (e: Exception) {
            releaseRecognizer()
        }
    }

    private fun releaseRecognizer() {
        val rec = speech ?: return
        speech = null
        try {
            rec.cancel()
        } catch (e: Exception) {
            // already stopped
        }
        try {
            rec.destroy()
        } catch (e: Exception) {
            // already destroyed
        }
    }

    private fun launchRecognizerDialog(language: String) {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        try {
            recognizerLauncher.launch(intent)
        } catch (e: Exception) {
            sttError?.invoke("service-not-allowed")
            clearSttCallbacks()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (applicationInfo.flags and android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE != 0) {
            // Lets chrome://inspect read the console and the page source of a
            // debug build, which is the difference between guessing at a
            // blank screen and reading the error that caused it.
            WebView.setWebContentsDebuggingEnabled(true)
        }

        val view = buildWebView()
        web = view

        setContentView(view)
        view.loadUrl(PAGE_URL)

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                // Read web, not the captured local: after a renderer restart
                // the original view is destroyed and asking it whether it can
                // go back is asking a corpse.
                val live = web
                if (live != null && live.canGoBack()) live.goBack() else finish()
            }
        })
    }

    private fun buildWebView(): WebView {
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        return WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            addJavascriptInterface(TtsBridge(), "AndroidTTS")
            addJavascriptInterface(SttBridge(), "AndroidSTT")
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(
                    view: WebView,
                    request: WebResourceRequest
                ): WebResourceResponse? = loader.shouldInterceptRequest(request.url)

                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean = request.url.host != "appassets.androidplatform.net"
            }
        }
    }

    /**
     * The renderer runs in its own process. When it is killed - out of memory
     * is the usual reason, and this app's page is heavy enough to be a
     * candidate on a constrained device - Android's default is to kill the
     * whole application with it. That is what "opens and immediately jumps
     * out of the app" was: not a JS error, and nothing in logcat to point at
     * the page, just the process disappearing.
     *
     * Returning true says the app has dealt with it. The dead view is
     * discarded, a fresh one is built and the page reloads, so the user sees a
     * reload instead of being thrown to the launcher.
     */
    override fun onRenderProcessGone(view: WebView, detail: RenderProcessGoneDetail): Boolean {
        releaseRecognizer()
        clearSttCallbacks()
        web = null
        try {
            (view.parent as? android.view.ViewGroup)?.removeView(view)
            view.destroy()
        } catch (ignored: Exception) {
            // the process is already gone; there is nothing left to clean up
        }
        // The microphone belongs to the dead renderer, not to us.
        try {
            Toast.makeText(
                this,
                "Reloading — Android stopped the page renderer",
                Toast.LENGTH_SHORT
            ).show()
        } catch (ignored: Exception) {
        }

        val fresh = buildWebView()
        web = fresh
        setContentView(fresh)
        fresh.loadUrl(PAGE_URL)
        return true
    }

    override fun onPause() {
        super.onPause()
        web?.onPause()
    }

    override fun onResume() {
        super.onResume()
        web?.onResume()
    }

    companion object {
        private const val PAGE_URL =
            "https://appassets.androidplatform.net/assets/www/index.html"
    }

    /** JS → native speech. Called from the page via window.AndroidTTS. */
    inner class TtsBridge {
        @JavascriptInterface
        fun speak(text: String?) {
            if (text.isNullOrBlank()) return
            runOnUiThread {
                val engine = tts
                if (engine != null && ttsReady) {
                    try {
                        // media stream = clearer, and honours the volume slider
                        engine.setAudioAttributes(
                            AudioAttributes.Builder()
                                .setUsage(AudioAttributes.USAGE_MEDIA)
                                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                                .build()
                        )
                        engine.language = Locale.UK
                        engine.setSpeechRate(0.95f)
                        engine.setPitch(1.0f)
                    } catch (ignored: Exception) {
                    }
                    engine.speak(text, TextToSpeech.QUEUE_FLUSH, null, "fluentify")
                }
            }
        }

        @JavascriptInterface
        fun stop() {
            runOnUiThread { tts?.stop() }
        }

        @JavascriptInterface
        fun isReady(): Boolean = ttsReady
    }

    /** JS → native speech recognition, the mirror image of the TTS bridge. */
    inner class SttBridge {
        /** Does this device have a usable recogniser at all? */
        @JavascriptInterface
        fun available(): Boolean {
            if (!SpeechRecognizer.isRecognitionAvailable(this@MainActivity)) return false
            // <queries> covers the recogniser intent for API 30+, so the
            // in-process path is reachable too.
            val i = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            return i.resolveActivity(packageManager) != null
        }

        @JavascriptInterface
        fun hasPermission(): Boolean =
            ContextCompat.checkSelfPermission(
                this@MainActivity, Manifest.permission.RECORD_AUDIO
            ) == PackageManager.PERMISSION_GRANTED

        /**
         * Begin recognition. The three callbacks are the JS functions
         * onPartial / onFinal / onError; each is invoked with a plain string
         * so the page never has to know about Android Bundle types.
         */
        @JavascriptInterface
        fun start(
            language: String?,
            onPartial: String?,
            onFinal: String?,
            onError: String?
        ) {
            sttLanguage = language ?: "en-GB"
            val w = web ?: return
            sttPartial = { text -> w.evaluateJavascript("window.$onPartial(${quote(text)})", null) }
            sttFinal = { text -> w.evaluateJavascript("window.$onFinal(${quote(text)})", null) }
            sttError = { code -> w.evaluateJavascript("window.$onError(${quote(code)})", null) }

            runOnUiThread {
                if (hasPermission()) {
                    startRecognizer(sttLanguage)
                } else {
                    micPermission.launch(Manifest.permission.RECORD_AUDIO)
                }
            }
        }

        @JavascriptInterface
        fun stop() {
            runOnUiThread { stopRecognizer() }
        }

        /** Tear the microphone down: called when the activity goes away. */
        fun release() {
            releaseRecognizer()
            clearSttCallbacks()
        }

        private fun quote(s: String): String {
            val sb = StringBuilder("\"")
            for (c in s) {
                when {
                    c == '"' -> sb.append("\\\"")
                    c == '\\' -> sb.append("\\\\")
                    c == '\n' -> sb.append("\\n")
                    c == '\r' -> sb.append("\\r")
                    c == '\t' -> sb.append("\\t")
                    // Char.toInt() is hidden on Kotlin 1.9; Char.code is the
                    // replacement and is a non-negative code point by contract.
                    c.code < 0x20 -> sb.append("\\u").append(
                        String.format(Locale.ROOT, "%04x", c.code)
                    )
                    else -> sb.append(c)
                }
            }
            return sb.append('"').toString()
        }
    }

    override fun onStart() {
        super.onStart()
        if (tts == null) {
            tts = TextToSpeech(this) { status ->
                ttsReady = status == TextToSpeech.SUCCESS
                if (ttsReady) tts?.language = Locale.UK
            }
        }
    }

    override fun onStop() {
        super.onStop()
        tts?.stop()
        // Backgrounded with the microphone open is how dictation used to end up
        // stuck: the page's stop() never arrived because the page was gone.
        releaseRecognizer()
    }

    override fun onDestroy() {
        super.onDestroy()
        tts?.shutdown()
        tts = null
        releaseRecognizer()
        clearSttCallbacks()
    }
}