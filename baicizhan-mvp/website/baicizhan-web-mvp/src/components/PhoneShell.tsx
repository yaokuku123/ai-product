// 百词斩 Web MVP - PhoneShell
// 用“手机容器”模拟 App 竖屏体验（桌面端也不违和）

import type { PropsWithChildren } from "react";
import { cn } from "@/lib/utils";

export default function PhoneShell({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-6">
      <div
        className={cn(
          "w-full max-w-[420px] rounded-[2.2rem] border border-border bg-card text-card-foreground shadow-[0_30px_90px_-50px_rgba(20,40,90,0.45)] overflow-hidden",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}
