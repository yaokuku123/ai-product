// 百词斩 Web MVP - TopBar
// iOS 风格搜索栏 + 右侧消息按钮

import { Bell, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TopBar({ title }: { title?: string }) {
  return (
    <div className="px-5 pt-5 pb-4 bg-card">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          {title ? <span className="font-display text-lg text-foreground">{title}</span> : null}
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 rounded-full"
          aria-label="消息"
          onClick={() => {
            // MVP：占位
          }}
        >
          <Bell className="h-5 w-5" />
        </Button>
      </div>

      <div className="mt-4 relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          className="w-full h-11 rounded-full border border-border bg-background pl-11 pr-4 text-sm outline-none focus:ring-2 focus:ring-ring/30"
          placeholder="查词（MVP 暂不支持搜索）"
          readOnly
        />
      </div>

      <div className="mt-3 text-xs text-muted-foreground">学习数据同步完成</div>
    </div>
  );
}
