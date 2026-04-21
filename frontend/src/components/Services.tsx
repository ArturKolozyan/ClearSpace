"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

const services = [
  {
    id: "houses",
    title: "Частные дома и квартиры",
    price: "от 3 500 ₽",
    description: "Комплексная уборка жилых помещений любой площади.",
    features: [
      "Сухая и влажная уборка",
      "Мытье окон и зеркал",
      "Обеспыливание поверхностей",
      "Дезинфекция санузлов",
    ],
  },
  {
    id: "cars",
    title: "Машины",
    price: "от 4 000 ₽",
    description: "Профессиональная химчистка салона автомобиля.",
    features: [
      "Чистка сидений",
      "Очистка потолка и пола",
      "Обработка пластика",
      "Устранение запахов",
    ],
  },
  {
    id: "furniture",
    title: "Мебель",
    price: "от 1 200 ₽",
    description: "Глубокая экстракторная чистка мягкой мебели.",
    features: [
      "Удаление сложных пятен",
      "Уничтожение пылевых клещей",
      "Чистка матрасов и диванов",
      "Антибактериальная обработка",
    ],
  },
];

type ApiPriceItem = {
  key: string;
  title: string;
  price_from: number;
};

type ApiPriceCategory = {
  key: string;
  items: ApiPriceItem[];
};

export default function Services() {
  const [prices, setPrices] = useState<Record<string, number>>({});
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

  useEffect(() => {
    const controller = new AbortController();
    const loadPrices = async () => {
      try {
        const response = await fetch(`${apiBase}/api/prices`, { signal: controller.signal });
        if (!response.ok) {
          return;
        }
        const data = (await response.json()) as ApiPriceCategory[];
        const servicesCategory = data.find((category) => category.key === "services");
        if (!servicesCategory) {
          return;
        }
        const nextPrices = servicesCategory.items.reduce<Record<string, number>>((acc, item) => {
          acc[item.key] = item.price_from;
          return acc;
        }, {});
        setPrices(nextPrices);
      } catch {
        // Keep static fallback prices if API is unavailable.
      }
    };
    void loadPrices();
    return () => controller.abort();
  }, [apiBase]);

  const servicesWithActualPrices = useMemo(
    () =>
      services.map((service) => ({
        ...service,
        price: `от ${(prices[service.id] ?? Number(service.price.replace(/\D/g, ""))).toLocaleString("ru-RU")} ₽`,
      })),
    [prices]
  );

  return (
    <section id="services" className="py-24 relative scroll-mt-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6 }}
            className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4"
          >
            Наши услуги
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-lg text-slate-600 text-balance"
          >
            Выберите подходящий тариф или закажите индивидуальный расчет стоимости.
          </motion.p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {servicesWithActualPrices.map((service, index) => (
            <motion.div
              key={service.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass-card flex flex-col h-full overflow-hidden text-center sm:text-left"
            >
              <div className="p-8 flex-grow flex flex-col items-center sm:items-start">
                <h3 className="text-2xl font-bold text-slate-900 mb-2">{service.title}</h3>
                <div className="text-3xl font-extrabold text-brand-blue mb-4">{service.price}</div>
                <p className="text-slate-600 mb-8 flex-grow">{service.description}</p>
                
                <ul className="space-y-4 mb-8 w-full text-left">
                  {service.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3 justify-center sm:justify-start">
                      <CheckCircle2 className="text-brand-mint shrink-0 mt-0.5" size={20} />
                      <span className="text-slate-700 text-sm leading-tight">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link
                  href="#contact"
                  className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-medium transition-all bg-slate-100 text-slate-700 hover:bg-slate-200"
                >
                  Оставить заявку
                  <ArrowRight size={18} />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}