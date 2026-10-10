plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "app.fluentify"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.fluentify"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        // The debug build is signed with the standard auto-generated Android
        // debug key, so the APK is directly installable on any device.
        debug {
            isMinifyEnabled = false
        }
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    // Serves the bundled www/ folder over https://appassets.androidplatform.net/
    // so fetch() for the JSON data files works inside the WebView.
    implementation("androidx.webkit:webkit:1.11.0")
}