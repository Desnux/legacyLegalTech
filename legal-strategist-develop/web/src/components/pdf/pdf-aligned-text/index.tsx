import { Text, View, StyleSheet } from "@react-pdf/renderer";

const styles = StyleSheet.create({
  container: {
    display: "flex",
    flexDirection: "column",
    width: "100%",
  },
  lineContainer: {
    flexDirection: "row",
    marginBottom: 4,
  },
  label: {
    fontWeight: "bold",
    flex: 3,
    textAlign: "left",
    paddingRight: 5,
  },
  value: {
    flex: 4,
    textAlign: "left",
  },
});

const PDFAlignedText = ({ text, style }: { text: string, style?: any }) => {
  const lines = text.trim().split("\n").map(line => {
    const [label, value] = line.split(" : ");
    return { label, value };
  });

  return (
    <View style={[styles.container, style]}>
      {lines.map((line, index) => (
        <View style={styles.lineContainer} key={index}>
          <Text style={styles.label}>{line.label}</Text>
          <Text style={styles.value}>: {line.value}</Text>
        </View>
      ))}
    </View>
  );
};

export default PDFAlignedText;
