import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import MetricsPanel from "../app/components/MetricsPanel";

describe("MetricsPanel", () => {
  const defaultProps = {
    decision:        "PASS",
    confidence:      0.85,
    retries:         0,
    retrieval_score: 0.5,
  };

  test("renders PASS decision in green", () => {
    render(<MetricsPanel {...defaultProps} />);
    const decision = screen.getByText("PASS");
    expect(decision).toBeInTheDocument();
    expect(decision).toHaveClass("text-green-500");
  });

  test("renders FAIL decision in red", () => {
    render(<MetricsPanel {...defaultProps} decision="FAIL" confidence={0.2} />);
    const decision = screen.getByText("FAIL");
    expect(decision).toBeInTheDocument();
    expect(decision).toHaveClass("text-red-500");
  });

  test("renders confidence as percentage", () => {
    render(<MetricsPanel {...defaultProps} confidence={0.85} />);
    expect(screen.getByText("85%")).toBeInTheDocument();
  });

  test("renders retry count correctly", () => {
    render(<MetricsPanel {...defaultProps} retries={2} />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  test("renders retrieval score as percentage", () => {
    render(<MetricsPanel {...defaultProps} retrieval_score={0.5} />);
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  test("renders Pipeline Metrics heading", () => {
    render(<MetricsPanel {...defaultProps} />);
    expect(screen.getByText("Pipeline Metrics")).toBeInTheDocument();
  });
});