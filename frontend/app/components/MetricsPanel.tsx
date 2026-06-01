// RAG pipeline ke metrics dikhata hai
// Decision, Confidence, Retries, Retrieval Score

interface Props {
  decision: string;
  confidence: number;
  retries: number;
  retrieval_score: number;
}

export default function MetricsPanel({ decision, confidence, retries, retrieval_score }: Props) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mt-4">
      <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">
        Pipeline Metrics
      </h3>

      <div className="grid grid-cols-2 gap-3">

        {/* Decision */}
        <div className="bg-white rounded-lg p-3 border">
          <p className="text-xs text-gray-500 mb-1">Decision</p>
          <span className={`text-sm font-bold ${
            decision === "PASS" ? "text-green-500" : "text-red-500"
          }`}>
            {decision}
          </span>
        </div>

        {/* Confidence */}
        <div className="bg-white rounded-lg p-3 border">
          <p className="text-xs text-gray-500 mb-1">Confidence</p>
          <p className="text-sm font-bold text-blue-500">
            {(confidence * 100).toFixed(0)}%
          </p>
        </div>

        {/* Retries */}
        <div className="bg-white rounded-lg p-3 border">
          <p className="text-xs text-gray-500 mb-1">Retries</p>
          <p className="text-sm font-bold text-orange-500">
            {retries}
          </p>
        </div>

        {/* Retrieval Score */}
        <div className="bg-white rounded-lg p-3 border">
          <p className="text-xs text-gray-500 mb-1">Retrieval Score</p>
          <p className="text-sm font-bold text-purple-500">
            {(retrieval_score * 100).toFixed(0)}%
          </p>
        </div>

      </div>
    </div>
  );
}