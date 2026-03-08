export function StatusPill(props: { label: string; tone?: "good" | "warn" | "bad" }) {
  const tone = props.tone || "good";
  return <span className={`status-pill ${tone}`}>{props.label}</span>;
}
