const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

async function main() {
    console.log("🌱 Seeding database...");

    // 1. Create Default User
    const user = await prisma.user.upsert({
        where: { email: "sergio@fbrapps.com" },
        update: {},
        create: {
            id: "default-user-id",
            email: "sergio@fbrapps.com",
            name: "Sergio",
            role: "ADMIN",
        },
    });

    // 2. Create Workspace
    const workspace = await prisma.workspace.upsert({
        where: { slug: "facebrasil" },
        update: {},
        create: {
            name: "Facebrasil",
            slug: "facebrasil",
        },
    });

    // 3. Create Space
    const space = await prisma.space.create({
        data: {
            workspaceId: workspace.id,
            name: "Marketing",
            description: "Espaço para coordenação de marketing",
        },
    });

    // 4. Create Channel
    const channel = await prisma.channel.create({
        data: {
            id: "general", // Matching the ID used in the UI
            spaceId: space.id,
            name: "Geral",
        },
    });

    console.log("✅ Seed complete!", {
        userId: user.id,
        workspaceId: workspace.id,
        spaceId: space.id,
        channelId: channel.id,
    });
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
