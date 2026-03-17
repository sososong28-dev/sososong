import Foundation

public enum PromptInjectionBuilder {
    public static func javascript(inputSelector: String, prompt: String) -> String {
        let escapedPrompt = prompt
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
            .replacingOccurrences(of: "\n", with: "\\n")

        return """
        (function() {
          const input = document.querySelector(\"\(inputSelector)\");
          if (!input) { return { ok: false, reason: \"input-not-found\" }; }
          input.value = \"\(escapedPrompt)\";
          input.dispatchEvent(new Event('input', { bubbles: true }));
          return { ok: true };
        })();
        """
    }
}
