/* Repositories, mirror first.
 *
 * maven.google.com and repo1.maven.org are unreachable from this network, so
 * the Myket mirror is listed first: it proxies maven.google.com, the Gradle
 * plugin portal, JitPack and Maven Central, and serves the bytes unchanged
 * (same SHA-1 as the origin). The official repositories stay in the list as a
 * fallback, so this still builds on a network that can reach them - and if the
 * mirror ever disagrees, Gradle tries the next entry rather than silently
 * taking the wrong artifact.
 */
pluginManagement {
    repositories {
        maven { url = uri("https://maven.myket.ir/") }
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        maven { url = uri("https://maven.myket.ir/") }
        google()
        mavenCentral()
    }
}

rootProject.name = "Fluentify"
include(":app")
