// 百词斩 Web MVP - WordDetail（单词详解页）
// 设计承诺：信息分层（Tabs）+ 强可读性 + 可返回做题

import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useRoute } from "wouter";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import PhoneShell from "@/components/PhoneShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { fetchWordDetail, type WordDetail } from "@/lib/api";

export default function WordDetailPage() {
  const [, params] = useRoute("/word/:id");
  const wordId = useMemo(() => Number(params?.id || 0), [params]);
  const [, setLocation] = useLocation();

  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<WordDetail | null>(null);

  useEffect(() => {
    if (!wordId) {
      setLocation("/");
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        const d = await fetchWordDetail(wordId);
        if (!cancelled) setDetail(d);
      } catch {
        toast.error("获取单词详情失败");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [wordId, setLocation]);

  return (
    <PhoneShell className="bg-card">
      <div className="px-5 pt-5 pb-4 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            返回首页
          </Link>
          <div className="text-sm text-muted-foreground">单词详解</div>
          <Button variant="ghost" size="sm" className="rounded-full" onClick={() => toast.message("MVP 暂不支持收藏")}
            >
            收藏
          </Button>
        </div>
      </div>

      <div className="px-5 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            加载中…
          </div>
        ) : detail ? (
          <>
            <div>
              <div className="font-display text-5xl leading-none">{detail.headword}</div>
              <div className="mt-2 text-sm text-muted-foreground">
                {detail.phonetic ? `${detail.phonetic} ` : ""}
                {detail.pos ? detail.pos : ""}
              </div>
              <div className="mt-3 text-lg font-semibold">{detail.meaning_zh}</div>
              {detail.meaning_en ? (
                <div className="mt-1 text-sm text-muted-foreground">{detail.meaning_en}</div>
              ) : null}
            </div>

            <Tabs defaultValue="example" className="mt-6">
              <TabsList className="grid grid-cols-3 w-full">
                <TabsTrigger value="example">例句</TabsTrigger>
                <TabsTrigger value="etymology">词根</TabsTrigger>
                <TabsTrigger value="more">更多</TabsTrigger>
              </TabsList>

              <TabsContent value="example" className="mt-4">
                <Card className="rounded-3xl p-5">
                  {detail.example_en ? (
                    <div className="text-sm leading-relaxed">{detail.example_en}</div>
                  ) : (
                    <div className="text-sm text-muted-foreground">暂无例句</div>
                  )}
                  {detail.example_zh ? (
                    <div className="mt-2 text-sm text-muted-foreground">{detail.example_zh}</div>
                  ) : null}
                </Card>
              </TabsContent>

              <TabsContent value="etymology" className="mt-4">
                <Card className="rounded-3xl p-5">
                  {detail.etymology ? (
                    <div className="text-sm leading-relaxed">{detail.etymology}</div>
                  ) : (
                    <div className="text-sm text-muted-foreground">暂无词源拆解</div>
                  )}
                </Card>
              </TabsContent>

              <TabsContent value="more" className="mt-4">
                <Card className="rounded-3xl p-5">
                  <div className="text-sm text-muted-foreground">形近/相关词（简单示例）</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {detail.similar_words.length ? (
                      detail.similar_words.map((w) => (
                        <span key={w} className="px-3 py-1 rounded-full bg-secondary text-sm">
                          {w}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-muted-foreground">暂无</span>
                    )}
                  </div>
                </Card>
              </TabsContent>
            </Tabs>

            <div className="mt-6">
              <Button className="w-full h-12 rounded-2xl" onClick={() => setLocation("/")}
                >
                回到首页
              </Button>
            </div>
          </>
        ) : null}
      </div>
    </PhoneShell>
  );
}
