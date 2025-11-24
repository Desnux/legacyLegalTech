import { Suggestion } from "@/services/response";


interface ResponseTextSuggestionsProps {
    suggestions: Suggestion[];
    setSelectedSuggestion: (suggestion: Suggestion) => void;
}

const ResponseTextSuggestions: React.FC<ResponseTextSuggestionsProps> = ({ suggestions, setSelectedSuggestion }) => {
  const maxScore = Math.max(...suggestions.map(s => s.score));
  const doNothingScore = 1.0 - maxScore;
  const suggestionsSum = suggestions.reduce((sum, doc) => sum + doc.score, 0);
  const totalScore = suggestionsSum + doNothingScore;
  
return (
    <div className="overflow-y-auto h-full pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
    <div className="flex items-center justify-between px-4 py-2 font-bold text-sm text-gray-700 border-b border-gray-200 mb-2">
      <span>Nombre</span>
      <span>Recomendación relativa</span>
    </div>
    <ul className="divide-y divide-gray-200">
      {suggestions.map((suggestion) => {
        const normalizedScore = totalScore > 0 ? suggestion.score / totalScore : 0;
        return (
          <li key={suggestion.id} className="py-2">
            <div
              className="flex items-center justify-between w-full px-4 py-2 hover:bg-gray-100 rounded-md cursor-pointer"
              onClick={() => setSelectedSuggestion(suggestion)}
            >
              <span className="flex-1">{suggestion.name}</span>
              <span className="text-right">
                {new Intl.NumberFormat("es-ES", {
                  style: "percent",
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                }).format(normalizedScore)}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  </div>
)
}

export default ResponseTextSuggestions;