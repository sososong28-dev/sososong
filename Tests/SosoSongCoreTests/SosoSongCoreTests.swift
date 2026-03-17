import XCTest
@testable import SosoSongCore

final class SosoSongCoreTests: XCTestCase {
    func testLoadProviders() throws {
        let providers = try ProviderCatalog().loadProviders()
        XCTAssertGreaterThanOrEqual(providers.count, 3)
        XCTAssertEqual(providers.first?.id, "openclaw")
    }

    func testPromptInjectionEscapesText() {
        let js = PromptInjectionBuilder.javascript(inputSelector: "textarea", prompt: "a\n\"b\"")
        XCTAssertTrue(js.contains("\\n"))
        XCTAssertTrue(js.contains("\\\"b\\\""))
    }

    func testArchiveStoreRoundTrip() throws {
        let tmp = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("archive-\(UUID().uuidString).json")
        let store = ConversationArchiveStore(fileURL: tmp)
        let entry = ArchivedConversation(providerID: "gpt", title: "t", content: "c")
        try store.append(entry)

        let all = try store.load()
        XCTAssertEqual(all.count, 1)
        XCTAssertEqual(all[0].providerID, "gpt")
    }
}
