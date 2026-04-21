"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import Link from "next/link";
import { Sparkles, ArrowRight } from "lucide-react";

export default function Hero() {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, 100]);
  const y2 = useTransform(scrollY, [0, 500], [0, -100]);

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20">
      {/* Background Bubbles */}
      <div className="absolute inset-0 -z-10 pointer-events-none overflow-hidden">
        <motion.div
          style={{ y: y1 }}
          className="absolute top-20 left-10 w-72 h-72 bg-brand-blue/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"
        />
        <motion.div
          style={{ y: y2 }}
          className="absolute top-40 right-10 w-72 h-72 bg-brand-mint/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"
        />
        <motion.div
          style={{ y: y1 }}
          className="absolute -bottom-8 left-40 w-72 h-72 bg-brand-lavender/20 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"
        />
      </div>

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/50 backdrop-blur-md border border-white/60 text-brand-blue font-medium text-sm mb-6 shadow-sm mx-auto">
            <Sparkles size={16} />
            <span>Профессиональный клининг в Новороссийске</span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-slate-900 tracking-tight mb-6 leading-tight text-balance mx-auto">
            Идеальная чистота <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-blue to-brand-lavender">
              без лишних забот
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 mb-8 max-w-2xl mx-auto text-balance">
            Доверьте уборку профессионалам. Эко-средства, фиксированная цена и гарантия качества на все виды услуг.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="#contact"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 text-base font-semibold text-white bg-brand-blue hover:bg-sky-500 rounded-2xl shadow-lg shadow-brand-blue/30 transition-all hover:-translate-y-1"
            >
              Оставить заявку
              <ArrowRight size={20} />
            </Link>
            <Link
              href="#services"
              className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-slate-700 bg-white/60 hover:bg-white/80 backdrop-blur-md border border-white/50 rounded-2xl shadow-sm transition-all hover:-translate-y-1"
            >
              Наши услуги
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}