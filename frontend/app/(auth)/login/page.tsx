export default function LoginPage() {
  return (
    <main className="auth-shell">
      <section className="auth-card stack">
        <div>
          <div className="eyebrow">FBR-CLICK</div>
          <div className="brand-mark">Base comercial conectada</div>
          <h1 className="page-title">Receba, organize e converta leads de todas as origens.</h1>
          <p className="muted">
            Leads aquecidos do 1FBR-Leads entram aqui junto com contatos vindos do site,
            redes sociais e outras fontes operacionais.
          </p>
        </div>
        <form action="/api/auth/login" method="post" className="form-stack">
          <input className="input" type="email" name="email" placeholder="Email" required />
          <input className="input" type="password" name="password" placeholder="Senha" required />
          <button className="button" type="submit">Entrar</button>
        </form>
      </section>
    </main>
  );
}
