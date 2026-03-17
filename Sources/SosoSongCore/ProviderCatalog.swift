import Foundation

public enum ProviderCatalogError: Error, LocalizedError {
    case resourceMissing
    case decodeFailed

    public var errorDescription: String? {
        switch self {
        case .resourceMissing:
            return "providers.json not found in bundle resources."
        case .decodeFailed:
            return "Unable to decode provider catalog JSON."
        }
    }
}

public final class ProviderCatalog {
    public init() {}

    public func loadProviders() throws -> [AIProvider] {
        guard let url = Bundle.module.url(forResource: "providers", withExtension: "json") else {
            throw ProviderCatalogError.resourceMissing
        }
        let data = try Data(contentsOf: url)
        do {
            return try JSONDecoder().decode([AIProvider].self, from: data)
        } catch {
            throw ProviderCatalogError.decodeFailed
        }
    }
}
