const root = document.getElementById("work");
const lede = document.getElementById("lede");

const countWords = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"];

function safeUrl(value) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:" || url.protocol === "http:") return url.href;
  } catch (error) {
    return null;
  }
  return null;
}

function safeAsset(value) {
  if (typeof value !== "string") return null;
  if (!value.startsWith("assets/") || value.includes("..") || value.includes("\\") || value.includes('"')) return null;
  return value;
}

function hostname(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch (error) {
    return "";
  }
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text;
  return node;
}

function shotPicture(image, alt, eager) {
  const picture = document.createElement("picture");
  const webp = safeAsset(image.webp);
  const fallback = safeAsset(image.fallback);
  if (webp) {
    const source = document.createElement("source");
    source.type = "image/webp";
    source.srcset = webp;
    picture.append(source);
  }
  const img = document.createElement("img");
  img.src = fallback || webp || "";
  img.alt = alt || "";
  img.width = image.width || 1440;
  img.height = image.height || 900;
  img.decoding = "async";
  if (eager) {
    img.loading = "eager";
    img.setAttribute("fetchpriority", "high");
  } else {
    img.loading = "lazy";
  }
  picture.append(img);
  return picture;
}

function responsiveShot(project, eager) {
  const desktop = project.images.desktop;
  const phone = project.images.phone;
  const picture = document.createElement("picture");
  const alt = (desktop && desktop.alt) || `${project.client} homepage`;

  if (phone && safeAsset(phone.webp)) {
    const source = document.createElement("source");
    source.media = "(max-width: 639px)";
    source.type = "image/webp";
    source.srcset = safeAsset(phone.webp);
    picture.append(source);
  }
  if (phone && safeAsset(phone.fallback)) {
    const source = document.createElement("source");
    source.media = "(max-width: 639px)";
    source.srcset = safeAsset(phone.fallback);
    picture.append(source);
  }
  if (desktop && safeAsset(desktop.webp)) {
    const source = document.createElement("source");
    source.type = "image/webp";
    source.srcset = safeAsset(desktop.webp);
    picture.append(source);
  }
  const img = document.createElement("img");
  img.src = safeAsset(desktop && desktop.fallback) || safeAsset(desktop && desktop.webp) || "";
  img.alt = alt;
  img.width = (desktop && desktop.width) || 1440;
  img.height = (desktop && desktop.height) || 900;
  img.decoding = "async";
  if (eager) {
    img.loading = "eager";
    img.setAttribute("fetchpriority", "high");
  } else {
    img.loading = "lazy";
  }
  picture.append(img);
  return picture;
}

function deviceBar(host) {
  const bar = el("div", "device-bar");
  const dots = el("span", "dots");
  dots.setAttribute("aria-hidden", "true");
  dots.append(el("i"), el("i"), el("i"));
  const url = el("span", "device-url", host);
  bar.append(dots, url);
  return bar;
}

function placeholder(client) {
  const frame = el("div", "pending");
  frame.setAttribute("role", "img");
  frame.setAttribute("aria-label", `Screenshot pending for ${client}`);
  frame.append(el("p", "pending-label", "Screenshot pending"));
  return frame;
}

function renderIndex(projects) {
  const nav = el("nav", "index");
  nav.setAttribute("aria-label", "Projects");
  const list = document.createElement("ol");
  projects.forEach((project) => {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `work/${project.slug}/`;
    const num = el("span", "index-num", project.number);
    link.append(num, document.createTextNode(project.shortName));
    item.append(link);
    list.append(item);
  });
  nav.append(list);
  return nav;
}

function renderProject(project, index) {
  const band = el("article", index % 2 === 1 ? "band is-flip" : "band");
  band.id = project.slug;

  const blur = project.images && safeAsset(project.images.blur);
  if (blur && !project.pending) {
    const bg = el("div", "band-bg");
    bg.style.backgroundImage = `url("${blur}")`;
    bg.setAttribute("aria-hidden", "true");
    band.append(bg);
  }
  band.append(el("div", "band-shade"));

  const grid = el("div", "grid band-grid");
  const copy = el("div", "copy");
  const kicker = el("p", "kicker");
  kicker.append(el("span", "num", project.number), document.createTextNode(" / " + project.shortName));
  const heading = el("h2", "client");
  heading.id = `${project.slug}-title`;
  const page = `work/${project.slug}/`;
  const titleLink = document.createElement("a");
  titleLink.href = page;
  titleLink.textContent = project.client;
  heading.append(titleLink);
  band.setAttribute("aria-labelledby", heading.id);
  copy.append(kicker, heading, el("p", "category", project.category));
  if (project.venture) copy.append(el("p", "venture", project.venture));
  copy.append(el("p", "outcome", project.headline));

  const href = safeUrl(project.url);
  const links = el("div", "card-links");
  const view = document.createElement("a");
  view.className = "visit";
  view.href = page;
  view.append(document.createTextNode("View project"));
  links.append(view);
  if (href) {
    const link = document.createElement("a");
    link.className = "visit";
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.append(document.createTextNode("Visit site"));
    const sr = el("span", "sr-only", `, ${project.client} (opens in a new tab)`);
    link.append(sr);
    const arrow = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    arrow.setAttribute("viewBox", "0 0 20 20");
    arrow.setAttribute("aria-hidden", "true");
    arrow.setAttribute("width", "18");
    arrow.setAttribute("height", "18");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M5 10h8.5M10.5 6.5 14 10l-3.5 3.5");
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "currentColor");
    path.setAttribute("stroke-width", "1.6");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");
    arrow.append(path);
    link.append(arrow);
    links.append(link);
  }
  copy.append(links);

  const stage = el("div", "stage");
  const showImages = !project.pending && project.images && project.images.desktop;
  if (showImages) {
    const figure = el("figure", "device");
    figure.append(deviceBar(hostname(href || "")));
    figure.append(responsiveShot(project, index === 0));
    const stageLink = document.createElement("a");
    stageLink.className = "stage-link";
    stageLink.href = page;
    stageLink.setAttribute("aria-label", `View the ${project.client} project`);
    stageLink.append(figure);
    stage.append(stageLink);
    if (project.images.phone) {
      const handset = el("figure", "handset");
      handset.setAttribute("aria-hidden", "true");
      handset.append(shotPicture(project.images.phone, "", false));
      stage.append(handset);
    }
  } else {
    stage.append(placeholder(project.client));
  }

  grid.append(copy, stage);
  band.append(grid);
  return band;
}

function spell(count) {
  if (count <= 10) return countWords[count];
  return String(count);
}

function render(projects) {
  root.replaceChildren();
  if (!Array.isArray(projects) || projects.length === 0) {
    root.append(el("p", "load-note", "No projects are listed yet."));
    return;
  }
  if (lede && !lede.dataset.ready) {
    const sentence = el(
      "span",
      null,
      ` ${spell(projects.length)} live site${projects.length === 1 ? "" : "s"} ${projects.length === 1 ? "is" : "are"} below, shown as ${projects.length === 1 ? "it is" : "they are"}.`
    );
    lede.append(sentence);
    lede.dataset.ready = "true";
  }
  root.append(renderIndex(projects));
  projects.forEach((project, index) => root.append(renderProject(project, index)));
}

fetch("projects.json")
  .then((response) => {
    if (!response.ok) throw new Error(String(response.status));
    return response.json();
  })
  .then((data) => render(data.projects))
  .catch(() => {
    root.replaceChildren(el("p", "load-note", "The project list did not load."));
  });
