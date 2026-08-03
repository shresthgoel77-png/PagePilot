import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const token = request.cookies.get('auth-token')?.value || request.cookies.get('access_token')?.value;

    const protectedPaths = ['/settings'];
    const isProtected = protectedPaths.some(p => request.nextUrl.pathname.startsWith(p));

    if (isProtected) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/settings/:path*'],
};
