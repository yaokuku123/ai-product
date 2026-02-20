// 百词斩 Web MVP - Home（仪表盘）
// 设计承诺：iOS Utility Minimalism / 大数字卡 + 单一强 CTA

import { useEffect, useMemo, useState } from "react";
import { Link, useLocation } from "wouter";
import { toast } from "sonner";

import PhoneShell from "@/components/PhoneShell";
import TopBar from "@/components/TopBar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { fetchPlan, startSession } from "@/lib/api";

export default function Home() {
  const [, setLocation] = useLocation();

  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState<Awaited<ReturnType<typeof fetchPlan>> | null>(null);

  const learnedPercent = useMemo(() => {
    if (!plan || plan.total_words <= 0) return 0;
    return Math.round((plan.learned_words / plan.total_words) * 100);
  }, [plan]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const p = await fetchPlan();
        if (!cancelled) setPlan(p);
      } catch (e) {
        toast.error("无法连接后端：请先启动 FastAPI (8001)");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function onStart() {
    try {
      const t = toast.loading("正在准备今日任务…");
      const { session_id } = await startSession();
      toast.dismiss(t);
      setLocation(`/study/${session_id}`);
    } catch (e) {
      toast.error("启动学习失败：请检查后端是否可用");
    }
  }

  return (
    <PhoneShell>
      <TopBar />

      <div className="px-5 pb-6">
        <Card className="rounded-3xl border-border/80 shadow-sm overflow-hidden">
          <div className="px-5 pt-5 pb-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-sm text-muted-foreground">今日单词</div>
                <div className="font-display text-5xl leading-none mt-1">
                  {loading ? "…" : plan?.daily_new ?? 20}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">剩余天数</div>
                <div className="font-display text-5xl leading-none mt-1">
                  {loading ? "…" : plan?.remaining_days ?? 0}
                </div>
              </div>
            </div>

            <div className="mt-5 flex items-center justify-between">
              <div>
                <div className="text-base font-semibold">四级高频（示例词库）</div>
                <div className="text-sm text-primary mt-0.5">查看实体书籍</div>
              </div>
              <Button variant="secondary" className="rounded-full h-10" onClick={() => toast.message("MVP 暂不支持调整计划")}
                >
                调整计划
              </Button>
            </div>

            <div className="mt-5">
              <div className="flex items-center justify-between text-sm">
                <div className="text-muted-foreground">学习进度</div>
                <div className="text-muted-foreground">
                  {plan ? `${plan.learned_words}/${plan.total_words}` : "—"}
                </div>
              </div>
              <div className="mt-2">
                <Progress value={learnedPercent} className="h-2" />
              </div>
              <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span className="inline-block h-2 w-2 rounded-full bg-primary" />
                  <span>单词数据</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-block h-2 w-2 rounded-full bg-muted" />
                  <span>单词列表</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          {plan ? `今日需新学 ${plan.daily_new}/${plan.daily_new}   今日需复习 0` : ""}
        </div>

        <div className="mt-4">
          <Button
            className="w-full h-14 rounded-2xl text-lg font-semibold shadow-[0_20px_40px_-25px_rgba(35,90,255,0.7)]"
            onClick={onStart}
          >
            开始背单词吧
          </Button>
        </div>

        <div className="mt-6 flex items-center justify-between text-xs text-muted-foreground">
          <Link href="/" className="hover:text-foreground">
            首页
          </Link>
          <span>复习</span>
          <span>小讲堂</span>
          <span>周边</span>
          <span>圈子</span>
        </div>
      </div>
    </PhoneShell>
  );
}
