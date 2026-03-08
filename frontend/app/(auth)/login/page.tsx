import { redirect } from "next/navigation";

import { getSession } from "@/lib/session";

export default async function LoginPage() {
  const session = await getSession();
  if (session.isLoggedIn) {
    redirect("/dashboard");
  }

  return (
    <main className="auth-shell">
      <section className="auth-card stack">
        <div className="stack">
          <span className="eyebrow">FBR-Leads</span>
          <div className="brand-mark">Outbound command center</div>
          <h1 className="page-title">Entrar no painel operacional</h1>
          <p className="muted">
            Sessao protegida por cookie httpOnly e todo trafego autenticado passa pelo proxy do Next.js.
          </p>
        </div>

        <form action="/api/auth/login" method="post" className="form-stack">
          <input className="input" type="email" name="email" placeholder="owner@facebrasil.test" required />
          <input className="input" type="password" name="password" placeholder="Sua senha" required />
          <button className="button" type="submit">Entrar</button>
        </form>
      </section>
    </main>
  );
}
