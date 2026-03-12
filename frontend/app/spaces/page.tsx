import { redirect } from "next/navigation";

import { getSpaceBundle } from "@/lib/server-api";

export default async function SpacesPage() {
  const { spaces, channels } = await getSpaceBundle();
  const firstSpace = spaces[0];
  const firstChannel = channels.find((channel) => channel.space_id === firstSpace?.id) ?? channels[0];

  if (!firstSpace || !firstChannel) {
    return <main className="main-content">Nenhum space ou canal disponivel ainda.</main>;
  }

  redirect(`/spaces/${firstSpace.id}/channels/${firstChannel.id}`);
}
