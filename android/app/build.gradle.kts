import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

/* ---- version ------------------------------------------------------------
 * An app updates in place only if its versionCode is higher than the one
 * already installed. This was hardcoded to 1, so every build after the first
 * carried the same number: Android treated it as the same release, and
 * anything that wanted a strict increase had nothing to give it. Package
 * managers answer "reinstall" and users lose their data.
 *
 * The number now lives in version.properties and is bumped automatically on
 * every assemble, so two builds can never collide. Bump it here, never in
 * build.gradle, or the next build will read whatever was written last.
 */
val versionFile = rootProject.file("version.properties")
val versionProps = Properties().apply {
    if (versionFile.exists()) versionFile.inputStream().use { load(it) }
}
var appVersionCode = versionProps.getProperty("versionCode", "1").toInt()
val appVersionName = versionProps.getProperty("versionName", "1.0")

/* Writes the next number back. Only ever increases, so an interrupted or
 * repeated build cannot walk the version backwards. */
fun bumpVersionCode() {
    appVersionCode += 1
    versionFile.writeText(
        "# Bumped automatically by assemble - see app/build.gradle.kts.\n" +
        "# This is the number the NEXT build will use, which is why it sits\n" +
        "# one ahead of the APK that was just built. Android only updates an\n" +
        "# app in place when its versionCode is higher than the installed\n" +
        "# one, so it must never repeat or go backwards.\n" +
        "versionCode=$appVersionCode\n" +
        "versionName=$appVersionName\n"
    )
}

/* Signing.
 *
 * The key has to be the SAME on every machine that builds this, or Android
 * refuses the install with INSTALL_FAILED_UPDATE_INCOMPATIBLE and the user
 * has to uninstall first - which is exactly the "update" turning into
 * "reinstall". That is not hypothetical: this app was installed signed with
 * one key and the next build came out signed with another, so the update was
 * rejected outright.
 *
 * So the key is pinned in the repository. It is a sideloaded, offline app and
 * this is not a Play Store upload key - committing it is what makes an update
 * from any checkout possible. keystore.properties still overrides it for a
 * real release build, and the passwords of THAT one are never committed.
 */
val keystoreProps = Properties().apply {
    val f = rootProject.file("keystore.properties")
    if (f.exists()) f.inputStream().use { load(it) }
}
val hasReleaseKeystore = keystoreProps.getProperty("storeFile") != null
val pinnedKeystore = rootProject.file("keystore/fluentify.p12")

android {
    namespace = "app.fluentify"
    compileSdk = 34

    defaultConfig {
        applicationId = "app.fluentify"
        minSdk = 24
        targetSdk = 34
        versionCode = appVersionCode
        versionName = appVersionName
    }

    signingConfigs {
        // Every build type signs with the pinned key, so debug and release
        // can also update one another on a device.
        create("pinned") {
            storeFile = pinnedKeystore
            storePassword = "fluentify"
            keyAlias = "fluentify"
            keyPassword = "fluentify"
        }
        if (hasReleaseKeystore) {
            create("release") {
                storeFile = rootProject.file(keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        debug {
            isMinifyEnabled = false
            signingConfig = if (hasReleaseKeystore) signingConfigs.getByName("release")
                            else signingConfigs.getByName("pinned")
        }
        release {
            isMinifyEnabled = false
            signingConfig = if (hasReleaseKeystore) signingConfigs.getByName("release")
                            else signingConfigs.getByName("pinned")
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

/* Bump once per assemble, before the variant is configured. Without this two
 * builds of the same tree would carry the same number and the second install
 * would be a reinstall. */
tasks.matching { it.name == "preBuild" }.configureEach {
    doFirst { bumpVersionCode() }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    // Serves the bundled www/ folder over https://appassets.androidplatform.net/
    // so fetch() for the JSON data files works inside the WebView.
    implementation("androidx.webkit:webkit:1.11.0")
}