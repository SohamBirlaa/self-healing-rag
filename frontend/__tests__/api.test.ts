global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

beforeEach(() => {
  jest.clearAllMocks();
  jest.resetModules();
});

describe("sendChat", () => {
  test("sends POST request to correct endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok:   true,
      json: async () => ({
        answer:          "Test answer",
        decision:        "PASS",
        confidence:      0.85,
        retries:         0,
        retrieval_score: 0.5,
      }),
    } as Response);

    const { sendChat } = await import("../lib/api");
    const result = await sendChat("What is this about?");

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/chat"),
      expect.objectContaining({ method: "POST" })
    );
    expect(result.answer).toBe("Test answer");
    expect(result.decision).toBe("PASS");
  });

  test("throws error on API failure", async () => {
    mockFetch.mockResolvedValueOnce({
      ok:         false,
      statusText: "Internal Server Error",
    } as Response);

    const { sendChat } = await import("../lib/api");
    await expect(sendChat("test")).rejects.toThrow();
  });
});

describe("getIngestStatus", () => {
  test("fetches status from correct endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok:   true,
      json: async () => ({ total_chunks: 24, message: "24 chunks indexed." }),
    } as Response);

    const { getIngestStatus } = await import("../lib/api");
    const result = await getIngestStatus();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/ingest/status")
    );
    expect(result.total_chunks).toBe(24);
  });
});

describe("getDocuments", () => {
  test("returns list of indexed documents", async () => {
    mockFetch.mockResolvedValueOnce({
      ok:   true,
      json: async () => ({ documents: ["file1.pdf", "file2.txt"], total: 2 }),
    } as Response);

    const { getDocuments } = await import("../lib/api");
    const result = await getDocuments();

    expect(result.documents).toHaveLength(2);
    expect(result.documents).toContain("file1.pdf");
  });
});

describe("clearDocuments", () => {
  test("sends DELETE request to clear endpoint", async () => {
    mockFetch.mockResolvedValueOnce({
      ok:   true,
      json: async () => ({ message: "Cleared." }),
    } as Response);

    const { clearDocuments } = await import("../lib/api");
    await clearDocuments();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/ingest/clear"),
      expect.objectContaining({ method: "DELETE" })
    );
  });
});