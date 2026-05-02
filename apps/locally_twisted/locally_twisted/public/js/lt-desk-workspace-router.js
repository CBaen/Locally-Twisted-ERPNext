(function () {
  var staleWorkspaceRoutes = {
    accounting: true,
    crm: true,
    home: true,
    projects: true,
    selling: true,
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
  }

  function isWorkspaceLikeRoute(routeName) {
    if (!routeName || routeName === "Workspaces") return false;
    return Boolean(staleWorkspaceRoutes[routeName] || frappe.workspaces[routeName]);
  }

  function useWorkspaceContainer(routeName) {
    if (!isWorkspaceLikeRoute(routeName)) return routeName;

    if (window.location.pathname !== "/app/Workspaces") {
      window.history.replaceState(null, "", "/app/Workspaces");
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

  seedWorkspaceRoutes();
  document.addEventListener("DOMContentLoaded", seedWorkspaceRoutes);
})();
