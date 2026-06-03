import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import MessageBubble from "../app/components/MessageBubble";

describe("MessageBubble", () => {
  test("renders user message on the right side", () => {
    render(<MessageBubble role="user" content="Hello!" />);
    expect(screen.getByText("Hello!")).toBeInTheDocument();
    expect(screen.getByText("U")).toBeInTheDocument();
  });

  test("renders assistant message on the left side", () => {
    render(<MessageBubble role="assistant" content="Hi there!" />);
    expect(screen.getByText("Hi there!")).toBeInTheDocument();
    expect(screen.getByText("AI")).toBeInTheDocument();
  });

  test("renders message content correctly", () => {
    const content = "This is a long answer about the project.";
    render(<MessageBubble role="assistant" content={content} />);
    expect(screen.getByText(content)).toBeInTheDocument();
  });

  test("user message has blue background", () => {
    const { container } = render(
      <MessageBubble role="user" content="Test" />
    );
    const bubble = container.querySelector(".bg-blue-500");
    expect(bubble).toBeInTheDocument();
  });

  test("assistant message has gray background", () => {
    const { container } = render(
      <MessageBubble role="assistant" content="Test" />
    );
    const bubble = container.querySelector(".bg-gray-100");
    expect(bubble).toBeInTheDocument();
  });
});