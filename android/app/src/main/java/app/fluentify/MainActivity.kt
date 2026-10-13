package app.fluentify

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.os.Bundle
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
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
                launchRecognizer(sttLanguage)
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

    private fun launchRecognizer(language: String) {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            // Streaming partials: the composer shows text while they speak
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

        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        val view = WebView(this).apply {
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
        web = view

        setContentView(view)
        view.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (view.canGoBack()) view.goBack() else finish()
            }
        })
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
                    launchRecognizer(sttLanguage)
                } else {
                    micPermission.launch(Manifest.permission.RECORD_AUDIO)
                }
            }
        }

        @JavascriptInterface
        fun stop() {
            // RecognizerIntent runs as its own activity; finishing it is the
            // only way to stop it, and only if it is actually up.
            sttError?.invoke("aborted")
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
    }

    override fun onDestroy() {
        super.onDestroy()
        tts?.shutdown()
        tts = null
    }
}