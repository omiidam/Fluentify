package app.fluentify

import android.annotation.SuppressLint
import android.media.AudioAttributes
import android.os.Bundle
import android.speech.tts.TextToSpeech
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

        val web = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            addJavascriptInterface(TtsBridge(), "AndroidTTS")
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
     */
    private fun applyBestEnglishVoice() {
        val engine = tts ?: return
        engine.setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build()
        )
        val preferred = listOf(
            "en-gb-x-rnn-local",   // on-device neural voices (most natural)
            "en-gb-x-nb-local",
            "en-us-x-rnn-local",
            "en-gb-x-sfg-local",
            "en-us-x-sfg-local",
            "en-gb"
        )
        val all = engine.voices ?: return
        for (name in preferred) {
            val v = all.firstOrNull { it.name == name }
            if (v != null && engine.setVoice(v)) {
                engine.language = Locale.UK
                return
            }
        }
        // otherwise: the highest-quality installed English voice
        val best = all
            .filter { it.locale.language == "en" }
            .maxByOrNull { q ->
                var s = 0
                if (q.quality >= TextToSpeech.QUALITY_NORMAL) s += 20
                if (q.quality >= TextToSpeech.QUALITY_HIGH) s += 40
                if (q.quality >= TextToSpeech.QUALITY_VERY_HIGH) s += 60
                if (!q.isNetworkConnectionRequired) s += 25   // offline
                if (q.locale.language == Locale.UK.language) s += 10
                s
            }
        if (best != null) engine.setVoice(best)
        else engine.language = Locale.UK
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