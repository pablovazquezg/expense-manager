# Expense Manager


> `expense-manager` is a utility that consolidates and categorizes all your income/expenses, and helps you get a clear picture of where your money comes from, and where it goes

![Shallow Backup GIF Demo](img/shallow-backup-demo.gif)

## Contents

 * [WHAT is this?](#what-is-this)
 * [HOW can it help me?](#why-would-I-use-this)
 * [HOW does it work?](#how-does-it-work)
 * [HOW can I use it?](#installation)
 * [WHAT else should I know or think about?](#git-integration)


## What is this?
'expense-manager' is a free tool that can:
1. Read all those transaction/activity .csv files you download from your bank and credit card companies (even if they are in different formats)
2. Consolidate all those transactions into a single, standardized view
3. Assign a type (i.e. credit/debit) and a category (e.g. groceries) to each of them (it comes with standard category list, which you could customize to meet your needs) which allows you to see exactly where your money comes from, and where it goes


## WHY would I use this?

`Context`: You find value in understanding how much money you are making, how much you are spending, and in which categories. It makes you feel in control, increases your financial awareness, and helps you gradually refine/improve your decision-making abilities. In other words, it contributes to your meta-goal in life: slowly but surely steer reality towards outcomes ranking higher in your personal preferences.

`Problem`: Your financial life has become quite complex, and you use multiple banking accounts and credit cards over any given period. You can easily download the activity/transactions for any of them, but **the .csv files you get are in slightly different formats**, and they either don't categorize your expenses, or they do but using different "buckets" and hierarchies. This makes the process time-consuming and error prone, and **you end up not doing it for months at a time or at all**.

`Solution:` With this utility, **you simply download the transactions for the period you want to analyze** (last month, year-to-date, last year, etc.), you drop the files in the input folder, you run a script, **and voilà!, you get a beautiful consolidated list with all the expenses categorized consistently**. This list is in .csv format, so you can easily analyze it using a tool like Excel (see the [ideas section](#ideas) to see what I do)

## HOW does it work?
### Process outline
1. Read all (.csv) files from the input folder and extract the key information required from each transaction (date, type, description, amount)
1. Consolidate all transactions into a single list; this typically involves some level of data wrangling.
1. The transaction descriptions (and only the descriptions) are sent in batches to an OpenAI LLM (gpt-3.5-turbo) which gives us the most appopriate category within our list (you can configure this list -- see the very next section for details)
1. This category is appended to each transaction, and the new description-category pairs from the LLM are stored into a reference file
1. In all future runs, the utility first looks up each description in this reference file. If it finds one that is similar enough, it picks up the associated category and it moves on to the next transaction; this materially reduces the number of API calls required over time, since many transactions are repetitive in nature (we are creatures of habit).
1. The final list of categorized transactions is saved into a .csv file

### Additional details and considerations
+ You'll need an OpenAI API key
+ `expense-manager` fully respects your privacy and doesn't collect any data at all. However, it does send the transaction descriptions (and only the descriptions) to an OpenAI LLM to obtain the associated category. OpenAI claims not to sell or use this data for any purposes, (starting on March 1st, 2023, not even to train their own models) but just be aware that's how the program works.
+ 
+ OpenAI key, fuzzy parameter, output file, how to create a pivot table, how to change categories, etc.

## HOW could I use this
---

> **NOTE:**
> `expense-manager` fully respects your privacy and doesn't collect any data at all. However, it does send the transaction descriptions (and only the descriptions) to an OpenAI LLM to obtain the associated category. OpenAI claims not to sell or use this data for any purposes, (starting on March 1st, 2023, not even to train their own models) but just be aware that's how the program works.

### Step 1: Understand the requirements
+ OpenAI API Key

#### Installation

```bash
$ git clone https://www.github.com/alichtman/shallow-backup.git
$ cd shallow-backup
$ pip3 install .
```

### Usage
---

To start the interactive program, simply run `$ shallow-backup`.

`shallow-backup` was built with scripting in mind. Every feature that's supported in the interactive program is supported with command line arguments.

```shell
Usage: shallow-backup [OPTIONS]

  Easily back up installed packages, dotfiles, and more.
  You can edit which files are backed up in ~/.shallow-backup.

  Written by Aaron Lichtman (@alichtman).

Options:
  --add-dot TEXT              Add a dotfile or dotfolder to config by path.
  -backup-all                 Full back up.
  -backup-configs             Back up app config files.
  -backup-dots                Back up dotfiles.
  -backup-packages            Back up package libraries.
  -delete-config              Delete config file.
  -destroy-backup             Delete backup directory.
  -dry-run                    Don't backup or reinstall any files, just give
                              verbose output.

  -backup-fonts               Back up installed fonts.
  --new-path TEXT             Input a new back up directory path.
  -no-new-backup-path-prompt  Skip setting new back up directory path prompt.
  -no-splash                  Don't display splash screen.
  -reinstall-all              Full reinstallation.
  -reinstall-configs          Reinstall configs.
  -reinstall-dots             Reinstall dotfiles and dotfolders.
  -reinstall-fonts            Reinstall fonts.
  -reinstall-packages         Reinstall packages.
  --remote TEXT               Set remote URL for the git repo.
  -separate-dotfiles-repo     Use if you are trying to maintain a separate
                              dotfiles repo and running into issue #229.

  -show                       Display config file.
  -v, --version               Display version and author info.
  -h, -help, --help           Show this message and exit.
```


### Git Integration
---

**A Word of Caution**

This backup tool is git-integrated, meaning that you can easily store your backups remotely (on GitHub, for example.) Dotfiles and configuration files may contain sensitive information like API keys and ssh keys, and you don't want to make those public. To make sure no sensitive files are uploaded accidentally, `shallow-backup` creates a `.gitignore` file if it can't find one in the directory. It excludes `.ssh/` and `.pypirc` by default. It's safe to remove these restrictions if you're pushing to a remote private repository, or you're only backing up locally. To do this, you should clear the `.gitignore` file without deleting it.

_If you choose to back up to a public repository, look at every file you're backing up to make sure you want it to be public._

**What if I'd like to maintain a separate repo for my dotfiles?**

`shallow-backup` makes this easy! After making your first backup, `cd` into the `dotfiles/` directory and run `$ git init`. Create a `.gitignore` and a new repo on your favorite version control platform. This repo will be maintained independently (manually) of the base `shallow-backup` repo. Note that you may need to use the `-separate_dotfiles_repo` flag to get this to work, and it may [break some other functionality of the tool](https://github.com/alichtman/shallow-backup/issues/229). It's ok for my use case, though.

Here's a `bash` script that I wrote to [automate my dotfile backup workflow](https://github.com/alichtman/scripts/blob/master/backup-and-update-dotfiles.sh). You can use this by placing it in your `$PATH`, making it executable, and running it.

### What can I back up?
---

By default, `shallow-backup` backs these up.

1. Dotfiles and dotfolders
    * `.bashrc`
    * `.bash_profile`
    * `.gitconfig`
    * `.pypirc`
    * `.config/shallow-backup.conf`
    * `.ssh/`
    * `.vim/`
    * `.zshrc`

2. App Config Files
    * Atom
    * VSCode
    * Sublime Text 2/3
    * Terminal.app

3. Installed Packages
    * `brew` and `cask`
    * `cargo`
    * `gem`
    * `pip`
    * `pip3`
    * `npm`
    * `macports`
    * `VSCode` Extensions
    * `Sublime Text 2/3` Packages
    * System Applications

4. User installed `fonts`.

### Configuration

If you'd like to modify which files are backed up, you have to edit the `JSON` config file, located at `~/.config/shallow-backup.conf`. There are two ways to do this.

1. Select the appropriate option in the CLI and follow the prompts.
2. Open the file in a text editor and make your changes.

Editing the file in a text editor will give you more control and be faster.

#### Conditional Backup and Reinstallation

> **Warning**
> This feature allows code execution (by design). If untrusted users can write to your config, they can achieve code execution next time you invoke `shallow-backup` _backup_ or _reinstall_ functions. Starting in `v5.2`, the config file will have default permissions of `644`, and a warning will be printed if others can write to the config.

Every key under dotfiles has two optional subkeys: `backup_condition` and `reinstall_condition`. Both of these accept expressions that will be evaluated with `bash`. An empty string (`""`) is the default value, and is considered to be `True`. If the return value of the expression is `0`, this is considered `True`. Otherwise, it is `False`. This lets you do simple things like preventing backup with:

```javascript
// Because `$ false` returns 1
"backup_condition": "false"
```

And also more complicated things like only backing up certain files if an environment variable is set:

```javascript
"backup_condition": "[[ -n \"$ENV_VAR\" ]]"
```

Here's an example config based on my [dotfiles](https://www.github.com/alichtman/dotfiles):

```json
{
	"backup_path": "~/shallow-backup",
	"lowest_supported_version": "5.0.0a",
	"dotfiles": {
		".config/agignore": {
			"backup_condition": "uname -a | grep Darwin",
			"reinstall_conditon": "uname -a | grep Darwin"
		},
		".config/git/gitignore_global": { },
		".config/jrnl/jrnl.yaml": { },
		".config/kitty": { },
		".config/nvim": { },
		".config/pycodestyle": { },
		...
		".zshenv": { }
	},
	"root-gitignore": [
		".DS_Store",
		"dotfiles/.config/nvim/.netrwhist",
		"dotfiles/.config/nvim/spell/en.utf-8.add",
		"dotfiles/.config/ranger/plugins/ranger_devicons",
		"dotfiles/.config/zsh/.zcompdump*",
		"dotfiles/.pypirc",
		"dotfiles/.ssh"
	],
	"dotfiles-gitignore": [
		".DS_Store",
		".config/nvim/.netrwhist",
		".config/nvim/spell/en.utf-8.add*",
		".config/ranger/plugins/*",
		".config/zsh/.zcompdump*",
		".config/zsh/.zinit",
		".config/tmux/plugins",
		".config/tmux/resurrect",
		".pypirc",
		".ssh/*"
	],
	"config_mapping": {
		"/Users/alichtman/Library/Application Support/Sublime Text 2": "sublime2",
		"/Users/alichtman/Library/Application Support/Sublime Text 3": "sublime3",
		"/Users/alichtman/Library/Application Support/Code/User/settings.json": "vscode/settings",
		"/Users/alichtman/Library/Application Support/Code/User/Snippets": "vscode/Snippets",
		"/Users/alichtman/Library/Application Support/Code/User/keybindings.json": "vscode/keybindings",
		"/Users/alichtman/.atom": "atom",
		"/Users/alichtman/Library/Preferences/com.apple.Terminal.plist": "terminal_plist"
	}
}
```

#### .gitignore

As of `v4.0`, any `.gitignore` changes should be made in the `shallow-backup` config file. `.gitignore` changes that are meant to apply to all directories should be under the `root-gitignore` key. Dotfile specific gitignores should be placed under the `dotfiles-gitignore` key. The original `default-gitignore` key in the config is still supported for backwards compatibility, however, converting to the new config format is strongly encouraged.

#### Output Structure
---

```shell
backup_dir/
├── configs
│   ├── plist
│   │   └── com.apple.Terminal.plist
│   ├── sublime_2
│   │   └── ...
│   └── sublime_3
│       └── ...
├── dotfiles
│   ├── .bash_profile
│   ├── .bashrc
│   ├── .gitconfig
│   ├── .pypirc
│   ├── ...
│   ├── .shallow-backup
│   ├── .ssh/
│   │   └── known_hosts
│   ├── .vim/
│   └── .zshrc
├── fonts
│   ├── AllerDisplay.ttf
│   ├── Aller_Bd.ttf
│   ├── ...
│   ├── Ubuntu Mono derivative Powerline Italic.ttf
│   └── Ubuntu Mono derivative Powerline.ttf
└── packages
    ├── brew-cask_list.txt
    ├── brew_list.txt
    ├── cargo_list.txt
    ├── gem_list.txt
    ├── installed_apps_list.txt
    ├── npm_list.txt
    ├── macports_list.txt
    ├── pip_list.txt
    └── sublime3_list.txt
```

### Reinstalling Dotfiles
----

To reinstall your dotfiles, clone your dotfiles repo and make sure your shallow-backup config path can be found at either `~/.config/shallow-backup.conf` or `$XDG_CONFIG_HOME/.shallow_backup.conf`. Set the `backup-path` key in the config to the path of your cloned dotfiles. Then run `$ shallow-backup -reinstall-dots`.

When reinstalling your dotfiles, the top level `.git/`, `.gitignore`, `img/` and `README.md` files and directories are ignored.

### Want to Contribute?
---

Check out `CONTRIBUTING.md` and the `docs` directory.