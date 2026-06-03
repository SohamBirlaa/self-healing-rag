import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import FileUpload from "../app/components/FileUpload";

jest.mock("../lib/api", () => ({
  uploadFile: jest.fn(),
}));

import { uploadFile } from "../lib/api";
const mockUploadFile = uploadFile as jest.MockedFunction<typeof uploadFile>;

describe("FileUpload", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders upload box with correct text", () => {
    render(<FileUpload />);
    expect(screen.getByText("Click to upload")).toBeInTheDocument();
    expect(screen.getByText("PDF, TXT, DOCX, MD")).toBeInTheDocument();
  });

  test("shows success message on successful upload", async () => {
    mockUploadFile.mockResolvedValueOnce({
      message:  "Success",
      chunks:   5,
      filename: "test.pdf",
    });

    render(<FileUpload />);

    const file  = new File(["content"], "test.pdf", { type: "application/pdf" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/uploaded/i)).toBeInTheDocument();
    });
  });

  test("shows error message on failed upload", async () => {
    mockUploadFile.mockRejectedValueOnce(new Error("File type not allowed"));

    render(<FileUpload />);

    const file  = new File(["content"], "test.exe", { type: "application/exe" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/File type not allowed/i)).toBeInTheDocument();
    });
  });

  test("renders Upload Document heading", () => {
    render(<FileUpload />);
    expect(screen.getByText("Upload Document")).toBeInTheDocument();
  });
});