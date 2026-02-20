// 百词斩 Web MVP - Study（背单词做题）
// 设计承诺：强 CTA + 题目居中 + 选项卡片 + 即时反馈

import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useRoute } from "wouter";
import { toast } from "sonner";
import { Loader2, Volume2 } from "lucide-react";

import PhoneShell from "@/components/PhoneShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { fetchNextWord, submitAnswer, type AnswerResult, type WordQuiz } from "@/lib/api";

export default function Study() {
  const [, params] = useRoute("/study/:sessionId");
  const sessionId = useMemo(() => Number(params?.sessionId || 0), [params]);
  const [, setLocation] = useLocation();

  const [loading, setLoading] = useState(true);
  const [quiz, setQuiz] = useState<WordQuiz | null>(null);

  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<AnswerResult | null>(null);

  const answered = !!result;

  async function loadNext() {
    try {
      setLoading(true);
      setSelected(null);
      setResult(null);
      const q = await fetchNextWord(sessionId);
      setQuiz(q);
    } catch (e: any) {
      const code = e?.response?.data?.detail;
      if (code === "no_more_words") {
        toast.success("今日任务完成啦")
        setLocation("/");
        return;
      }
      toast.error("获取下一题失败：请检查后端");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!sessionId) {
      setLocation("/");
      return;
    }
    loadNext();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function onSubmit(optionId: number) {
    if (!quiz || answered) return;
    try {
      setSelected(optionId);
      const r = await submitAnswer(sessionId, quiz.word_id, optionId);
      setResult(r);
    } catch {
      toast.error("提交失败");
    }
  }

  const head = quiz?.headword || "";
  const chunk = useMemo(() => {
    if (!head) return { a: "", b: "" };
    const mid = Math.ceil(head.length / 2);
    return { a: head.slice(0, mid), b: head.slice(mid) };
  }, [head]);

  return (
    <PhoneShell className="bg-card">
      <div className="px-5 pt-5 pb-4 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            返回
          </Link>
          <div className="text-sm text-muted-foreground">需新学 · 今日</div>
          <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full" aria-label="发音" onClick={() => toast.message("MVP 暂不提供 TTS")}
            >
            <Volume2 className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <div className="px-5 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            加载中…
          </div>
        ) : quiz ? (
          <>
            <div className="text-center">
              <div className="font-display text-[64px] leading-none tracking-tight text-primary">
                {chunk.a}
                <span className="text-foreground">{chunk.b}</span>
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                {quiz.pos ? `${quiz.pos} ` : ""}
                {quiz.phonetic || ""}
              </div>
              <div className="mt-4 text-xs text-muted-foreground">
                请选择最符合该单词含义的选项
              </div>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-3">
              {quiz.options.map((o) => {
                const isChosen = selected === o.id;
                const isCorrect = result?.correct_option_id === o.id;
                const show = answered;

                return (
                  <button
                    key={o.id}
                    className={cn(
                      "group relative rounded-2xl border border-border bg-background px-4 py-4 text-left transition-all",
                      "hover:border-ring/40 hover:shadow-sm",
                      isChosen && !show ? "border-ring shadow-sm" : "",
                      show && isCorrect ? "border-emerald-400/50 bg-emerald-50" : "",
                      show && isChosen && !isCorrect ? "border-red-400/50 bg-red-50" : ""
                    )}
                    onClick={() => onSubmit(o.id)}
                    disabled={answered}
                  >
                    <div className="text-base font-medium leading-snug">{o.text}</div>
                    <div className="mt-2 h-1 w-14 rounded-full bg-muted group-hover:bg-muted-foreground/20" />

                    {show && isCorrect ? (
                      <div className="absolute right-4 top-4 text-xs font-semibold text-emerald-700">正确</div>
                    ) : null}
                    {show && isChosen && !isCorrect ? (
                      <div className="absolute right-4 top-4 text-xs font-semibold text-red-700">错误</div>
                    ) : null}
                  </button>
                );
              })}
            </div>

            {result ? (
              <Card className="mt-6 rounded-3xl border-border/80 bg-card p-5">
                <div className="text-sm text-muted-foreground">单词详解</div>
                <div className="mt-2 text-xl font-semibold">
                  {quiz.headword} <span className="text-muted-foreground">{quiz.phonetic}</span>
                </div>
                <div className="mt-2 text-base">{result.meaning_zh}</div>

                {result.etymology ? (
                  <div className="mt-3 text-sm text-muted-foreground">{result.etymology}</div>
                ) : null}

                {result.example_en ? (
                  <div className="mt-4 rounded-2xl bg-secondary p-4">
                    <div className="text-sm font-medium">例句</div>
                    <div className="mt-1 text-sm text-foreground">{result.example_en}</div>
                    {result.example_zh ? (
                      <div className="mt-1 text-sm text-muted-foreground">{result.example_zh}</div>
                    ) : null}
                  </div>
                ) : null}

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <Button variant="secondary" className="rounded-2xl" onClick={loadNext}>
                    继续做题
                  </Button>
                  <Button
                    className="rounded-2xl"
                    onClick={() => setLocation(`/word/${quiz.word_id}`)}
                  >
                    查看完整释义
                  </Button>
                </div>
              </Card>
            ) : (
              <div className="mt-6 flex items-center justify-between gap-3">
                <Button variant="secondary" className="rounded-2xl flex-1" onClick={() => toast.message("MVP 暂不提供‘斩’逻辑，默认都要答")}
                  >
                  斩
                </Button>
                <Button variant="secondary" className="rounded-2xl flex-1" onClick={() => toast.message("提示：先根据词根/例句猜，再确认")}
                  >
                  提示
                </Button>
              </div>
            )}
          </>
        ) : null}
      </div>
    </PhoneShell>
  );
}
