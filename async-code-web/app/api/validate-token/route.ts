import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:5000';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        console.log('[validate-token] Forwarding request to backend:', BACKEND_URL);

        const response = await fetch(`${BACKEND_URL}/validate-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        console.log('[validate-token] Backend response status:', response.status);

        const data = await response.json();

        return NextResponse.json(data, { status: response.status });
    } catch (error) {
        console.error('[validate-token] Error details:', error);

        // Provide more specific error message
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        const detailedError = `Failed to connect to backend service at ${BACKEND_URL}: ${errorMessage}`;

        return NextResponse.json(
            {
                error: detailedError,
                status: 'error'
            },
            { status: 500 }
        );
    }
}
