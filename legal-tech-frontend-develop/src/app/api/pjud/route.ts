import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const baseURL = "https://oficinajudicialvirtual.pjud.cl/home/index.php";

  return new NextResponse(JSON.stringify({ answer: "Test" }), {
    status: 200,
  });
}
