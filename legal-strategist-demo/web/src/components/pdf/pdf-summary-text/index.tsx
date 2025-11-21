import { Text, View, StyleSheet } from "@react-pdf/renderer";

const styles = StyleSheet.create({
  text: {
    lineHeight: 1.75,
  },
  bold: {
    fontWeight: "bold",
  },
});

const PDFSummaryText = ({ text, style = {} }: { text: string, style?: any }) => {
  const lines = text.trim().split(';').filter(Boolean);

  return (
    <View style={[style]}>
      <Text>
        {lines.map((line, index) => {
          const [boldText, regularText] = line.split(":");
          return (
            <Text key={index} style={styles.text}>
              <Text style={styles.bold}>{boldText.trim()}:</Text>{" "}
              <Text>{regularText?.trim()}</Text>{index !== lines.length - 1 && "; "}
            </Text>
          );
        })}
      </Text>
    </View>
  );
};

export default PDFSummaryText;
