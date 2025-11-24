import React from "react";
import { Text, View } from "@react-pdf/renderer";

const DEFAULT_BOLD_WORDS = [
  "POR TANTO",
  "POR LO TANTO",
  "Ruego a US.",
  "RUEGO A US.",
  "SOLICITO A US.",
];

interface PDFParagraphTextProps {
  text: string;
  boldWords?: string[];
  style?: any;
}

const PDFParagraphText = ({ text, boldWords = DEFAULT_BOLD_WORDS, style = {} }: PDFParagraphTextProps) => {
  const regex = new RegExp(`(${boldWords.map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, "g");
  const paragraphs = text.split("\n\n");

  return (
    <>
      {paragraphs.map((paragraph, index) => {
        const parts = paragraph.split(regex);
        return (
          <View key={index} style={[ { lineHeight: 1 }, style]}>
            <Text style={{ marginBottom: 3 }}>
              {parts.map((part, i) => {
                if (regex.test(part)) {
                  return (
                    <Text key={i} style={{ fontWeight: "bold" }}>{part}</Text>
                  );
                }
                return <Text key={i}>{part}</Text>;
              })}
            </Text>
          </View>
        );
      })}
    </>
  );
};

export default PDFParagraphText;
