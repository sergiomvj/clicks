import prisma from "@/shared/lib/prisma";

export async function saveMessage(data: {
    channelId: string;
    userId: string;
    content: string;
    parentId?: string;
    isThread?: boolean;
}) {
    return await prisma.message.create({
        data: {
            channelId: data.channelId,
            userId: data.userId,
            content: data.content,
            parentId: data.parentId,
            isThread: data.isThread || false,
        },
        include: {
            user: {
                select: {
                    name: true,
                    image: true,
                    role: true,
                },
            },
        },
    });
}

export async function getChannelMessages(channelId: string) {
    return await prisma.message.findMany({
        where: {
            channelId,
            parentId: null, // Only top-level messages
        },
        include: {
            user: {
                select: {
                    name: true,
                    image: true,
                    role: true,
                },
            },
        },
        orderBy: {
            createdAt: "asc",
        },
    });
}
