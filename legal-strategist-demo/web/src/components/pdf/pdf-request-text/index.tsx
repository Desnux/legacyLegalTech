import React from "react";
import { Text, View } from "@react-pdf/renderer";

const DEFAULT_BOLD_WORDS = [
  "POR TANTO",
  "POR LO TANTO",
  "Ruego a US.",
  "RUEGO A US.",
  "SOLICITO A US.",
];

interface RequestTextProps {
  text: string;
  boldWords?: string[];
  style?: any;
}

const PDFRequestText = ({ text, boldWords = DEFAULT_BOLD_WORDS, style = {} }: RequestTextProps) => {
  const regex = new RegExp(`(${boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, "g");
  const paragraphs = text.split("\n\n");

  return (
    <>
      {paragraphs.map((paragraph, index) => {
        const hasColon = paragraph.includes(":");
        const [boldText, regularText] = hasColon ? paragraph.split(/:((.|\n)+)/) : [null, paragraph];

        return (
          <View key={index} style={[{ lineHeight: 1.75, marginBottom: 9 }, style]}>
            <Text style={{ marginBottom: 3 }}>
              {hasColon && boldText && (
                <Text style={{ fontWeight: "bold" }}>
                  {boldText}:{" "}
                </Text>
              )}
              <Text style={{ marginBottom: 3 }}>
                {regularText && regularText.trim().split("\n").map((line, i) => (
                  <React.Fragment key={i}>
                    {line.split(regex).map((part, j) => {
                      return regex.test(part) ? (
                        <Text key={j} style={{ fontWeight: "bold" }}>{part}</Text>
                      ) : (
                        <Text key={j}>{part}</Text>
                      );
                    })}
                    {i !== regularText.trim().split("\n").length - 1 && <Text style={{ marginBottom: 3 }}>{"\n"}</Text>} {/* New line between lines */}
                  </React.Fragment>
                ))}
              </Text>
            </Text>
          </View>
        );
      })}
    </>
  );
};

export default PDFRequestText;
