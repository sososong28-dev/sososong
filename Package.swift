// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "sososong",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v16),
        .macOS(.v13)
    ],
    products: [
        .library(name: "SosoSongCore", targets: ["SosoSongCore"]),
        .executable(name: "sososong-cli", targets: ["SosoSongCLI"])
    ],
    targets: [
        .target(
            name: "SosoSongCore",
            resources: [.process("Resources")]
        ),
        .executableTarget(
            name: "SosoSongCLI",
            dependencies: ["SosoSongCore"]
        ),
        .testTarget(
            name: "SosoSongCoreTests",
            dependencies: ["SosoSongCore"]
        )
    ]
)
