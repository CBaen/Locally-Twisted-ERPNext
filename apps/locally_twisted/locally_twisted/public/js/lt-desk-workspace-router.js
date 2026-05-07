(function () {
  var defaultWorkspaceTitle = "Owner Home";
  var staleWorkspaceRoutes = {
    accounting: defaultWorkspaceTitle,
    crm: defaultWorkspaceTitle,
    home: defaultWorkspaceTitle,
    "owner-home": defaultWorkspaceTitle,
    projects: defaultWorkspaceTitle,
    selling: defaultWorkspaceTitle,
  };

  function getWorkspaceSlug(value) {
    if (!value) return "";
    if (window.frappe && frappe.router && frappe.router.slug) {
      return frappe.router.slug(value);
    }
    return String(value)
      .trim()
      .toLowerCase()
      .replace(/[^\w\s-]/g, "")
      .replace(/\s+/g, "-");
  }

  function seedWorkspaceRoutes() {
    if (!window.frappe || !frappe.boot || !frappe.boot.allowed_workspaces) return;

    frappe.workspaces = frappe.workspaces || {};

    frappe.boot.allowed_workspaces.forEach(function (workspace) {
      if (!workspace || !workspace.name || !workspace.title) return;

      var routeData = {
        title: workspace.title,
        public: Boolean(workspace.public),
      };

      frappe.workspaces[getWorkspaceSlug(workspace.name)] = routeData;
      frappe.workspaces[getWorkspaceSlug(workspace.title)] = routeData;
    });

    rewriteStaleWorkspaceRoute();
    installPageviewGuard();
    scrubPlatformChrome();
  }

  function getWorkspaceRouteData(routeName) {
    if (!routeName) return null;
    return frappe.workspaces[routeName] || null;
  }

  function getTargetWorkspaceTitle(routeName) {
    var staleTarget = staleWorkspaceRoutes[routeName];
    if (staleTarget) return staleTarget;

    var routeData = getWorkspaceRouteData(routeName);
    return routeData && routeData.title;
  }

  function rememberWorkspaceTarget(title) {
    if (!title) return;
    localStorage.current_page = title;
    localStorage.is_current_page_public = "true";
  }

  function isWorkspaceLikeRoute(routeName) {
    if (!routeName || routeName === "Workspaces") return false;
    return Boolean(getTargetWorkspaceTitle(routeName));
  }

  function useWorkspaceContainer(routeName) {
    if (!isWorkspaceLikeRoute(routeName)) return routeName;

    var targetTitle = getTargetWorkspaceTitle(routeName);
    rememberWorkspaceTarget(targetTitle);

    var targetPath = "/app/Workspaces/" + encodeURIComponent(targetTitle);
    if (window.location.pathname !== targetPath) {
      window.history.replaceState(null, "", targetPath);
    }

    return "Workspaces";
  }

  function rewriteStaleWorkspaceRoute() {
    var appPrefix = "/app/";
    var path = window.location.pathname;
    if (!path.startsWith(appPrefix)) return;

    var currentSlug = decodeURIComponent(path.slice(appPrefix.length).split("/")[0] || "");
    useWorkspaceContainer(currentSlug);
  }

  function installPageviewGuard() {
    if (
      !window.frappe ||
      !frappe.views ||
      !frappe.views.pageview ||
      frappe.views.pageview._ltWorkspaceGuardInstalled
    ) {
      return;
    }

    var originalShow = frappe.views.pageview.show;
    var originalWithPage = frappe.views.pageview.with_page;

    frappe.views.pageview.show = function (routeName) {
      return originalShow.call(this, useWorkspaceContainer(routeName));
    };

    frappe.views.pageview.with_page = function (routeName, callback) {
      return originalWithPage.call(this, useWorkspaceContainer(routeName), callback);
    };

    frappe.views.pageview._ltWorkspaceGuardInstalled = true;
  }

  function scrubPlatformChrome() {
    var blockedLabels = [
      "ERPNext Settings",
      "ERPNext Integrations",
      "Frappe School",
      "Frappe Support",
    ];

    blockedLabels.forEach(function (label) {
      document.querySelectorAll("a, button, li, .dropdown-item").forEach(function (element) {
        if ((element.textContent || "").indexOf(label) !== -1) {
          var row = element.closest("li, .dropdown-item, .sidebar-item-container") || element;
          row.remove();
        }
      });
    });
  }

  seedWorkspaceRoutes();
  document.addEventListener("DOMContentLoaded", seedWorkspaceRoutes);
  document.addEventListener("click", function () {
    window.setTimeout(scrubPlatformChrome, 0);
  });
})();
