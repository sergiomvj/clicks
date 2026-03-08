export default function IcpPage() {
  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">ICP</span>
        <h1 className="page-title">Configuracao no-code do perfil ideal</h1>
        <p className="muted">Pagina pronta para receber form completo com setores, cargos, regioes e score minimo.</p>
      </div>
      <article className="surface-card form-stack">
        <input className="input" defaultValue="Empresas Brasileiras nos EUA" placeholder="Nome do ICP" />
        <input className="input" defaultValue="Diretor de Marketing, CEO" placeholder="Cargos alvo" />
        <input className="input" defaultValue="Florida, Texas, New York" placeholder="Regioes" />
        <button className="button" type="button">Salvar ICP</button>
      </article>
    </section>
  );
}
