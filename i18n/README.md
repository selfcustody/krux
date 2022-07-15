## Translation

Translations can be done for:

- UI: see `i18n/translations`
- Documentation: `i18n/README.md`

### Documentation

Steps:

- install [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n) plugin;
- configure translation;
- make a translation;

#### Installing mkdocs-static-i18n

In terminal, execute:

```
$> pip install mkdocs-static-i18n
```

#### Configure translation

Open `mkdocs.yml` and edit:

- `nav` section
- `plugins` section

##### Editing `nav` section

Supose you translated to [Lorem ipsum](https://en.wikipedia.org/wiki/Vulcan_(Star_Trek)).

First, you'll add an appropriate entry to `Home` subsection

```
nav:
  - Home:
    - index.en.md
    - index.lo.md
```

Now you will create a `index.lo.md` in `docs/` folder:

```
---
hide:
    - navigation
    - toc
---

# Krux
<img srcset="img/logo-150.png" align="right">

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Vitae congue mauris rhoncus aenean vel. Ridiculus mus mauris vitae ultricies leo integer. Mi ipsum faucibus vitae aliquet nec.

Aliquet lectus proin nibh nisl condimentum id venenatis. Ultrices tincidunt arcu non sodales. 

Consectetur lorem donec massa sapien faucibus et molestie ac.
```

##### Editing `plugins` section

Add an entry to `plugins.i18n.languages`:

```
plugins:
  ...
  - i18n:
    default_language: en
    languages:
      en: English
      lo:
        name: Lorem ipsum
        site_name: Krux - Adipiscing enim eu turpis egestas pretium aenean pharetra.
```

Add entries to `plugins.i18n.nav_translations`:

```
plugins:
  ...
  - i18n:
    ...
    nav_translations:
      Home: Ut ornare
      Getting Started: Lectus sit
      Part List: Amet est
      FAQ: Tempus urna
      Support the project: Et pharetra 
```
