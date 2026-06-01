// user and AI ke message alag alag dikhata hai

interface Props {
    role: "user" | "assistant";
    content: string;
}

export default function MessageBubble({role,content}: Props){
    const isUser = role == "user";

    return(
        <div className={`flex ${isUser ? "justify-end": "justify-start"} mb-4`}>
            {/*Avatar*/}
            <div className={`flex items-start gap-2 max-w-[80%] ${isUser ? "flex-row-reverse" : "flex-row"}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${isUser ? "bg-blue-500 text-white" : "bg-green-500 text-white"}`}>
                    {isUser ? "U" : "AI"}
                </div>
            {/*Message bubble*/}
            <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                isUser
                  ? "bg-blue-500 text-white rounded-none"
                  : "bg-gray-100 text-gray-800 rounded-tl-none"
            }`}>
                {content}
            </div>
            </div>
        </div>
    );
}
