import Foundation
import SosoSongCore

@main
struct SosoSongCLI {
    static func main() throws {
        let catalog = ProviderCatalog()
        let providers = try catalog.loadProviders()

        print("Loaded providers: \(providers.count)")
        for item in providers {
            print("- \(item.displayName): \(item.homeURL.absoluteString)")
        }

        let js = PromptInjectionBuilder.javascript(inputSelector: "textarea", prompt: "请总结今天工作，3个要点")
        print("\nInjection JS Preview:\n\(js.prefix(120))...")

        let archiveURL = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
            .appendingPathComponent(".sososong-history.json")
        let store = ConversationArchiveStore(fileURL: archiveURL)
        try store.append(.init(providerID: "gpt", title: "Demo", content: "This is a demo archived response."))
        let all = try store.load()
        print("\nArchived conversations: \(all.count)")
    }
}
