import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
    '/login(.*)',
    '/signup(.*)',
    '/api/webhooks(.*)',
    '/_next(.*)',
    '/favicon.ico',
    '/'
]);

export default clerkMiddleware(async (auth, req) => {
    if (process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_BYPASS_CLERK === 'true') {
        return;
    }
    if (!isPublicRoute(req)) {
        await auth.protect();
    }
});

export const config = {
    matcher: [
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        '/(api|trpc)(.*)',
    ],
};
