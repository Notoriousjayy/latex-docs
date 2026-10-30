import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Files;

/** Demonstrates normalized path containment. Not race-safe against hostile symlink mutations. */
public final class PathGuard {
    private PathGuard() {}

    public static Path underRoot(Path trustedRoot, String untrustedName) throws IOException {
        if (untrustedName == null || untrustedName.isBlank()) {
            throw new IllegalArgumentException("Name required");
        }
        Path input = Path.of(untrustedName);
        if (input.isAbsolute()) throw new SecurityException("Absolute path disallowed");
        Path root = trustedRoot.toRealPath(); // root must exist
        Path candidate = root.resolve(input).normalize();
        if (!candidate.startsWith(root)) throw new SecurityException("Traversal blocked");
        // Do not treat this check as a secure open against hostile concurrent writers.
        return candidate;
    }

    public static void main(String[] args) throws Exception {
        Path root = Files.createTempDirectory("pathguard-");
        Path ok = underRoot(root, "subdir/file.txt");
        if (!ok.startsWith(root.toRealPath())) throw new AssertionError("Contained expected");
        try {
            underRoot(root, "../outside.txt");
            throw new AssertionError("Expected traversal block");
        } catch (SecurityException expected) { /* pass */ }
        System.out.println("PathGuard tests passed");
    }
}
