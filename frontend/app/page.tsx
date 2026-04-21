"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { gsap } from "gsap";

type PriceItem = {
  title: string;
  price_from: number;
};

type PriceCategory = {
  key: string;
  title: string;
  accent: "teal" | "sand";
  items: PriceItem[];
};

type LeadForm = {
  name: string;
  phone: string;
  comment: string;
};

const services = [
  "Уборка квартир и домов",
  "Экспресс-уборка офисов",
  "Химчистка мягкой мебели",
  "Гипоаллергенная обработка",
];

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function Home() {
  const [prices, setPrices] = useState<PriceCategory[]>([]);
  const [hoveredSide, setHoveredSide] = useState<string | null>(null);
  const [form, setForm] = useState<LeadForm>({ name: "", phone: "", comment: "" });
  const [status, setStatus] = useState<"idle" | "sending" | "success" | "error">("idle");

  useEffect(() => {
    gsap.fromTo(
      ".reveal",
      { y: 32, opacity: 0 },
      { y: 0, opacity: 1, stagger: 0.12, duration: 0.8, ease: "power3.out" },
    );
  }, []);

  useEffect(() => {
    fetch(`${apiBase}/api/prices`)
      .then((res) => res.json())
      .then((data: PriceCategory[]) => setPrices(data))
      .catch(() => setPrices([]));
  }, []);

  const pricing = useMemo(
    () => ({
      left: prices.find((item) => item.accent === "teal") ?? null,
      right: prices.find((item) => item.accent === "sand") ?? null,
    }),
    [prices],
  );

  const submitLead = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!form.name.trim() || !form.phone.trim()) {
      setStatus("error");
      return;
    }
    setStatus("sending");
    try {
      const response = await fetch(`${apiBase}/api/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name.trim(),
          phone: form.phone.trim(),
          comment: form.comment.trim(),
        }),
      });
      if (!response.ok) {
        throw new Error("Lead request failed");
      }
      setStatus("success");
      setForm({ name: "", phone: "", comment: "" });
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none bubble bubble-1" />
      <div className="pointer-events-none bubble bubble-2" />
      <div className="pointer-events-none bubble bubble-3" />
      <header className="reveal sticky top-4 z-30 mx-auto mt-4 flex w-[92%] max-w-6xl items-center justify-between rounded-2xl border border-white/40 bg-white/30 px-4 py-3 backdrop-blur-xl md:px-8">
        <div className="text-lg font-semibold tracking-wide text-cyan-950">ClearSpace</div>
        <nav className="hidden items-center gap-8 text-cyan-950 md:flex">
          <a href="#services">Услуги</a>
          <a href="#pricing">Прайс</a>
          <a href="#contact">Контакты</a>
        </nav>
        <button className="glass-btn hidden md:block">Заказать звонок</button>
      </header>

      <main className="mx-auto flex w-[92%] max-w-6xl flex-col gap-10 pb-16 pt-8 md:pt-14">
        <section className="reveal grid gap-8 rounded-3xl border border-white/45 bg-white/20 p-6 backdrop-blur-xl md:grid-cols-2 md:p-10">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.3em] text-cyan-900/70">Premium cleaning service</p>
            <h1 className="text-4xl font-semibold leading-tight text-cyan-950 md:text-6xl">
              Чистота, которую можно почувствовать
            </h1>
            <p className="max-w-xl text-cyan-950/80 md:text-lg">
              Профессиональный клининг и химчистка с вниманием к деталям.
            </p>
            <a className="water-btn inline-flex" href="#pricing">
              Рассчитать стоимость
            </a>
          </div>
          <div className="relative min-h-72 rounded-3xl bg-gradient-to-br from-cyan-100/60 via-white/50 to-blue-200/60 p-6">
            <div className="orb orb-a" />
            <div className="orb orb-b" />
            <div className="orb orb-c" />
          </div>
        </section>

        <section id="services" className="reveal rounded-3xl border border-white/45 bg-white/20 p-6 backdrop-blur-xl md:p-10">
          <h2 className="mb-6 text-3xl font-semibold text-cyan-950">Услуги</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {services.map((service) => (
              <article key={service} className="service-card rounded-2xl border border-white/60 bg-white/35 p-5 text-cyan-950 shadow-sm">
                <h3 className="text-xl font-medium">{service}</h3>
                <p className="mt-2 text-sm text-cyan-950/70">
                  Профессиональные средства, проверенный персонал и гарантия результата.
                </p>
              </article>
            ))}
          </div>
        </section>

        <section id="pricing" className="reveal overflow-hidden rounded-3xl border border-white/45 bg-white/20 backdrop-blur-xl">
          <div className="grid md:grid-cols-2">
            <div
              onMouseEnter={() => setHoveredSide("left")}
              onMouseLeave={() => setHoveredSide(null)}
              className={`p-6 transition-all duration-300 md:p-10 ${hoveredSide === "right" ? "blur-[2px] opacity-70" : ""} bg-cyan-300/40`}
            >
              <h2 className="text-3xl font-semibold text-cyan-950 uppercase">{pricing.left?.title ?? "Клининг"}</h2>
              <div className="mt-6 space-y-4">
                {(pricing.left?.items ?? []).map((item) => (
                  <div key={item.title} className="flex items-center justify-between rounded-xl bg-white/55 px-4 py-3 text-cyan-950">
                    <span>{item.title}</span>
                    <span>от {item.price_from} ₽</span>
                  </div>
                ))}
              </div>
            </div>

            <div
              onMouseEnter={() => setHoveredSide("right")}
              onMouseLeave={() => setHoveredSide(null)}
              className={`p-6 transition-all duration-300 md:p-10 ${hoveredSide === "left" ? "blur-[2px] opacity-70" : ""} bg-amber-50/70`}
            >
              <h2 className="text-3xl font-semibold text-cyan-950 uppercase">{pricing.right?.title ?? "Химчистка"}</h2>
              <div className="mt-6 space-y-4">
                {(pricing.right?.items ?? []).map((item) => (
                  <div key={item.title} className="flex items-center justify-between rounded-xl bg-white/70 px-4 py-3 text-cyan-950">
                    <span>{item.title}</span>
                    <span>от {item.price_from} ₽</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="contact" className="reveal rounded-3xl border border-white/45 bg-white/20 p-6 backdrop-blur-xl md:p-10">
          {status === "success" ? (
            <div className="rounded-2xl bg-white/60 p-8 text-center text-cyan-950">
              <p className="text-2xl font-semibold">Ваша заявка принята, мастер уже в пути!</p>
            </div>
          ) : (
            <form className="grid gap-4 md:grid-cols-2" onSubmit={submitLead}>
              <input
                className="glass-input"
                placeholder="Имя"
                value={form.name}
                onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              />
              <input
                className="glass-input"
                placeholder="Телефон"
                value={form.phone}
                onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))}
              />
              <textarea
                className="glass-input md:col-span-2"
                placeholder="Комментарий"
                rows={3}
                value={form.comment}
                onChange={(event) => setForm((prev) => ({ ...prev, comment: event.target.value }))}
              />
              <button className="water-btn w-full md:col-span-2" type="submit" disabled={status === "sending"}>
                {status === "sending" ? "Отправляем..." : "Оставить заявку"}
              </button>
              {status === "error" ? (
                <p className="text-sm text-red-700 md:col-span-2">Проверьте поля и попробуйте снова.</p>
              ) : null}
            </form>
          )}
        </section>
      </main>
    </div>
  );
}
