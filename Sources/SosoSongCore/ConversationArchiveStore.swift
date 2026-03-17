import Foundation

public final class ConversationArchiveStore {
    private let fileURL: URL
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    public init(fileURL: URL) {
        self.fileURL = fileURL
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    }

    public func save(_ items: [ArchivedConversation]) throws {
        let data = try encoder.encode(items)
        try data.write(to: fileURL, options: .atomic)
    }

    public func load() throws -> [ArchivedConversation] {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            return []
        }
        let data = try Data(contentsOf: fileURL)
        return try decoder.decode([ArchivedConversation].self, from: data)
    }

    public func append(_ conversation: ArchivedConversation) throws {
        var all = try load()
        all.insert(conversation, at: 0)
        try save(all)
    }
}
