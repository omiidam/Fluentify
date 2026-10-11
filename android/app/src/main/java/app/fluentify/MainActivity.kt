package app.fluentify

import android.annotation.SuppressLint
import android.media.AudioAttributes
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.speech.tts.Voice
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader
import java.util.Locale

/**
 * Fluentify runs fully offline: the whole UI and the chatbot engine live in
 * assets/www. The asset loader exposes them over
 * https://appassets.androidplatform.net/ so that fetch("data/memory.json") is
 * same-origin and is not blocked by the stricter file:// origin rules.
 *
 * The 🎧 Listening panel speaks through Android's built-in text-to-speech
 * engine via the AndroidTTS bridge (fully offline, no network, no API key);
 * on the web build the page falls back to the Web Speech API.
 */
class MainActivity : AppCompatActivity() {

    private var tts: TextToSpeech? = null
    private var ttsReady = false

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        val bridge = TtsBridge()
        val web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            addJavascriptInterface(bridge, "AndroidTTS")
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

        setContentView(web)
        web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (web.canGoBack()) web.goBack() else finish()
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
                    engine.language = Locale.UK
                    engine.setSpeechRate(0.92f)
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

    override fun onStart() {
        super.onStart()
        if (tts == null) {
            tts = TextToSpeech(this) { status ->
                ttsReady = status == TextToSpeech.SUCCESS
                if (ttsReady) applyBestEnglishVoice()
            }
        }
    }

    /**
     * Route speech through the media stream (clearer, honours the volume
     * slider like a music app) and pick the most natural installed voice.
     * Written with plain loops and wrapped in try/catch: a missing voice on an
     * odd device must never take the app down.
     */
    private fun applyBestEnglishVoice() {
        val engine = tts ?: return
        try {
            engine.setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            val voices = engine.voices
            if (voices != null) {
                val all = ArrayList(voices)

                // 1) on-device neural voices sound the most natural
                val preferred = arrayOf(
                    "en-gb-x-rnn-local",
                    "en-gb-x-nb-local",
                    "en-us-x-rnn-local",
                    "en-gb-x-sfg-local",
                    "en-us-x-sfg-local",
                    "en-gb"
                )
                for (i in preferred.indices) {
                    val wanted = preferred[i]
                    for (j in all.indices) {
                        val v = all[j]
                        if (v.name == wanted && engine.setVoice(v)) {
                            engine.language = Locale.UK
                            return
                        }
                    }
                }

                // 2) otherwise the highest-quality installed English voice
                var best: Voice? = null
                var bestScore = -1
                for (j in all.indices) {
                    val v = all[j]
                    if (v.locale.language != "en") continue
                    var score = 0
                    if (v.quality >= TextToSpeech.QUALITY_VERY_HIGH) score += 60
                    if (v.quality >= TextToSpeech.QUALITY_HIGH) score += 40
                    if (v.quality >= TextToSpeech.QUALITY_NORMAL) score += 20
                    if (!v.isNetworkConnectionRequired) score += 25   // offline
                    if (score > bestScore) {
                        bestScore = score
                        best = v
                    }
                }
                val chosen = best
                if (chosen != null) engine.setVoice(chosen) else engine.language = Locale.UK
            } else {
                engine.language = Locale.UK
            }
        } catch (e: Exception) {
            try { engine.language = Locale.UK } catch (ignored: Exception) { }
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