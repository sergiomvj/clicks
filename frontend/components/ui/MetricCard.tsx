export function MetricCard(props: { label: string; value: string; hint: string }) {
  return (
    <article className="surface-card stack">
      <span className="metric-label">{props.label}</span>
      <strong className="metric-value">{props.value}</strong>
      <span className="muted">{props.hint}</span>
    </article>
  );
}
