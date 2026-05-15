const DEFAULT_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const FALLBACK_MODEL = "@cf/meta/llama-3.1-8b-instruct";

function envValue(...names) {
  for (const name of names) {
    if (process.env[name]) return process.env[name];
  }
  return "";
}

function buildDecisionPrompt(body) {
  const assets = Array.isArray(body.assets) ? body.assets.slice(0, 6) : [];
  const stack = body.stack || {};
  const consequences = stack.consequences || body.consequences || {};
  const scenario = body.scenario || "baseline";
  const assetLines = assets.map((asset, index) => (
    `${index + 1}. ${asset.id} ${asset.name}: area=${asset.area}, class=${asset.cls}, risk=${asset.adjustedRisk ?? asset.risk}%, health=${asset.health}%, rul=${asset.rul}d, esg=${asset.esg}%, action=${asset.action}`
  )).join("\n");

  return `You are the Morupule Predictive Intelligence decision advisor. Use the 5 Layer Decision Stack to produce a concise operational decision brief.

Decision stack:
- State: ${stack.state || "asset condition, location, class, current risk, health, RUL and ESG signal"}
- Time: ${stack.time || "trend and intervention window based on remaining useful life and scenario pressure"}
- Causality: ${stack.causality || "failure precursors, operating load, vibration, missingness and energy stress explain risk movement"}
- Simulation: ${stack.simulation || "what-if scenario filters adjust risk, downtime and energy exposure"}
- Consequence model: ${consequences.intervention || "compare do-nothing and intervention paths through operational KPIs"}
- Optimization: ${stack.optimization || "prioritize actions that reduce downtime, risk and avoidable energy loss within constraints"}

Scenario: ${scenario}
Current asset facts:
${assetLines || "No filtered assets were provided."}

Consequence reasoning:
- Do nothing: ${consequences.doNothing || "Estimate the downstream effect of inaction from the asset facts."}
- Planned action: ${consequences.plannedAction || "Estimate the downstream effect of the recommended intervention."}
- Propagation chain: ${Array.isArray(consequences.propagation) ? consequences.propagation.map(([title, detail]) => `${title}: ${detail}`).join(" | ") : "asset condition -> infrastructure dependency -> operational KPI -> resource constraint -> recommended action"}
- Objectives: ${Array.isArray(consequences.objectives) ? consequences.objectives.join(", ") : "reliability, safety, cost, ESG, resilience"}
- Constraints: ${Array.isArray(consequences.constraints) ? consequences.constraints.join(", ") : "budget, spares, crew, access, SHE controls, human approval"}

Return exactly these sections:
1. Decision summary
2. Why it is happening
3. Consequence comparison
4. Optimized action plan
5. Human approval boundary

Be specific to Morupule Coal Mine. Compare the do-nothing path against the planned intervention. Do not claim this is actual MCM confidential data; say it is real public data proxy-mapped for PoC when needed.`;
}

async function runCloudflare(model, accountId, token, prompt) {
  const response = await fetch(`https://api.cloudflare.com/client/v4/accounts/${accountId}/ai/run/${model}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages: [
        {
          role: "system",
          content: "You are a governed industrial AI advisor for reliability, maintenance, ESG, and operational decision intelligence. Be concise, practical, and clear about uncertainty.",
        },
        { role: "user", content: prompt },
      ],
      max_tokens: 650,
      temperature: 0.35,
      top_p: 0.9,
    }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.success === false) {
    const message = data?.errors?.[0]?.message || data?.message || `Cloudflare AI HTTP ${response.status}`;
    throw new Error(message);
  }
  return data?.result?.response || data?.response || JSON.stringify(data?.result || data);
}

export default async function handler(req, res) {
  if (req.method === "GET") {
    return res.status(200).json({
      ok: true,
      provider: "Cloudflare Workers AI",
      model: envValue("CLOUDFLARE_AI_MODEL", "CF_AI_MODEL") || DEFAULT_MODEL,
      accountConfigured: Boolean(envValue("CLOUDFLARE_ACCOUNT_ID", "CF_ACCOUNT_ID")),
      tokenConfigured: Boolean(envValue("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_AUTH_TOKEN", "CF_API_TOKEN")),
    });
  }

  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const accountId = envValue("CLOUDFLARE_ACCOUNT_ID", "CF_ACCOUNT_ID");
  const token = envValue("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_AUTH_TOKEN", "CF_API_TOKEN");
  const model = envValue("CLOUDFLARE_AI_MODEL", "CF_AI_MODEL") || DEFAULT_MODEL;

  if (!accountId || !token) {
    return res.status(500).json({
      error: "Cloudflare Workers AI is not configured. Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN, CLOUDFLARE_AUTH_TOKEN, or CF_API_TOKEN in Vercel environment variables.",
    });
  }

  try {
    const prompt = buildDecisionPrompt(req.body || {});
    let text;
    let modelUsed = model;
    try {
      text = await runCloudflare(model, accountId, token, prompt);
    } catch (error) {
      if (model === FALLBACK_MODEL) throw error;
      text = await runCloudflare(FALLBACK_MODEL, accountId, token, prompt);
      modelUsed = FALLBACK_MODEL;
    }
    return res.status(200).json({ provider: "Cloudflare Workers AI", model: modelUsed, response: text });
  } catch (error) {
    return res.status(502).json({ error: error.message || "Cloudflare Workers AI request failed" });
  }
}
