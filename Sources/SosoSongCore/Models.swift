import Foundation

public struct AIProvider: Codable, Equatable, Identifiable {
    public let id: String
    public let displayName: String
    public let homeURL: URL
    public let inputSelector: String
    public let submitSelector: String

    public init(id: String, displayName: String, homeURL: URL, inputSelector: String, submitSelector: String) {
        self.id = id
        self.displayName = displayName
        self.homeURL = homeURL
        self.inputSelector = inputSelector
        self.submitSelector = submitSelector
    }
}

public struct BrowserSession: Equatable, Identifiable {
    public enum StoreType: String, Equatable {
        case persistent
        case nonPersistent
    }

    public let id: UUID
    public let providerID: String
    public let accountLabel: String
    public let storeType: StoreType

    public init(id: UUID = UUID(), providerID: String, accountLabel: String, storeType: StoreType) {
        self.id = id
        self.providerID = providerID
        self.accountLabel = accountLabel
        self.storeType = storeType
    }
}

public struct ArchivedConversation: Codable, Equatable, Identifiable {
    public let id: UUID
    public let providerID: String
    public let title: String
    public let content: String
    public let createdAt: Date

    public init(id: UUID = UUID(), providerID: String, title: String, content: String, createdAt: Date = Date()) {
        self.id = id
        self.providerID = providerID
        self.title = title
        self.content = content
        self.createdAt = createdAt
    }
}
