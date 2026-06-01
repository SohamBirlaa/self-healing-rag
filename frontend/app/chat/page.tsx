import ChatBox from "../components/ChatBox";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-53px)] bg-white">
      <div className="flex-1 flex flex-col bg-white">
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <h2 className="text-sm font-semibold text-gray-700">Chat</h2>
          <p className="text-xs text-gray-400">Apne documents ke baare mein kuch bhi pucho</p>
        </div>
        <div className="flex-1 overflow-hidden bg-white">
          <ChatBox />
        </div>
      </div>
    </div>
  );
}