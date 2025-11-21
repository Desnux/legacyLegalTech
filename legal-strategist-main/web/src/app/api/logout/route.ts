import { NextResponse } from "next/server";
import { removeAuthToken, removeUserGroup } from "@/utils/auth-token";

export async function POST(request: Request) {
  const res = NextResponse.json({ ok: true });
  removeAuthToken(res);
  removeUserGroup(res);
  return res;
}
