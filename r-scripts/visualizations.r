library(ggplot2)
library(readr)
library(readxl)
library(dplyr)

ready_table_spain <- "./output/articles_sp_monthly_summary.csv"
ready_table_argentina <- "./output/articles_arg_monthly_summary.csv"

# X-axis: Year-Month and Y-axis: number of articles
visualize <- function(input_dataset, output_png, title) {
  figure <- read_csv(input_dataset, show_col_types = FALSE)
  figure <- figure[order(figure[["Year-Month"]]), ]
  figure[["Year-Month"]] <- factor(
    figure[["Year-Month"]],
    levels = unique(figure[["Year-Month"]])
  )

  plot <- ggplot(figure, aes(x = `Year-Month`)) +
    geom_col(
      aes(y = N_articles_total, fill = "Total"),
      width = 0.9
    ) +
    geom_col(
      aes(y = N_articles_filtered, fill = "Filtered"),
      width = 0.9
    ) +
    geom_col(
      aes(y = N_articles_used, fill = "Used"),
      width = 0.9
    ) +
    scale_fill_manual(
      values = c(
        "Total" = "darkblue",
        "Filtered" = "royalblue",
        "Used" = "lightblue"
      ),
      breaks = c("Total", "Filtered", "Used"),
      name = NULL
    ) +
    labs(
      x = "Year-Month",
      y = "Number of articles",
      title = title
    ) +
    theme_minimal(base_size = 14) + 
    theme(
      #panel.background = element_rect(fill = "#EAEAF2", color = NA),
      #plot.background = element_rect(fill = "white", color = NA),
      panel.grid.major = element_line(color = "white", linewidth = 0.7),
      panel.grid.minor = element_line(color = "white", linewidth = 0.35),
      axis.text.x = element_text(angle = 0, vjust = 0.5, hjust = 0.5)
    )

  ggsave(output_png, plot = plot, width = 11, height = 9, dpi=300, units = "in", scale=1)
}

visualize(
  ready_table_spain,
  "./output/plots/timelines/articles_sp_timeline.png",
  "Spain articles chronological order"
)
visualize(
  ready_table_argentina,
  "./output/plots/timelines/articles_arg_timeline.png",
  "Argentina articles chronological order"
)


# HEATMAPS
keyword_overlap_spain_input <-
  "./output/article-filtering/articles_sp_meta_2024-08-22_renewable-energy_green-hydrogen_selection-nov24.xlsx"
keyword_overlap_argentina_input <-
  "./output/article-filtering/articles_arg_meta_2024-08-22_renewable-energy_green-hydrogen_revisadoLW_jun25.xlsx"

prepare_keyword_data <- function(input_excel) {
  article_data <- read_excel(input_excel)
  keyword_columns <- grep("^keyword_", names(article_data), value = TRUE)

  other_keyword_columns <- setdiff(keyword_columns, "keyword_conflicto")
  
  keyword_data <- article_data |> 
    select(all_of(other_keyword_columns))

  any_keyword_match <- rowSums(keyword_data, na.rm = TRUE) > 0

  keyword_data <- keyword_data[any_keyword_match, ]

  return(keyword_data)
}

compute_keyword_overlap <- function(keyword_data) {
  keyword_matrix <- as.matrix(keyword_data)
  storage.mode(keyword_matrix) <- "numeric"

  co_occurrence_counts <- crossprod(keyword_matrix)
  keyword_totals <- colSums(keyword_matrix)

  overlap_matrix <- sweep(co_occurrence_counts, 1, keyword_totals, "/")
  overlap_matrix[keyword_totals == 0, ] <- NA_real_
  
  return(overlap_matrix)
}

plot_keyword_overlap_heatmap <- function(input_excel, output_png, title_use) {
  filtered_keyword_data <- prepare_keyword_data(input_excel)
  overlap_matrix <- compute_keyword_overlap(filtered_keyword_data)
  keyword_labels <- sub("^keyword_", "", colnames(overlap_matrix))

  plot_data <- as.data.frame(as.table(overlap_matrix), stringsAsFactors = FALSE)
  names(plot_data) <- c("keyword_a", "keyword_b", "proportion")

  plot_data$keyword_a <- factor(
    sub("^keyword_", "", plot_data$keyword_a),
    levels = keyword_labels
  )
  plot_data$keyword_b <- factor(
    sub("^keyword_", "", plot_data$keyword_b),
    levels = keyword_labels
  )
  plot_data$label <- ifelse(
    is.na(plot_data$proportion),
    "",
    paste0(round(plot_data$proportion * 100), "%")
  )
  plot_data$text_color <- ifelse(
    is.na(plot_data$proportion),
    "black",
    ifelse(plot_data$proportion >= 0.5, "white", "black")
  )

  plot_data <- plot_data |> 
    mutate(
      label = if_else(keyword_a == keyword_b, "-", label)
    )

  heatmap_plot <- ggplot(plot_data, aes(x = keyword_b, y = keyword_a, fill = proportion)) +
    geom_tile(color = "white", linewidth = 0.4) +
    geom_text(
      aes(label = label, color = text_color),
      size = 3
    ) +  
    scale_fill_gradient(
      low = "#F7FBFF",
      high = "#08306B",
      limits = c(0, 1),
      na.value = "grey90",
      labels = function(values) paste0(round(values * 100), "%"),
      name = "Overlap"
    ) +
    scale_colour_identity() + 
    labs(
      x = "Keywords",
      y = "Keywords",
      title = get("title_use", envir=environment())
    ) +
    coord_fixed() +
    theme_minimal(base_size = 14) +
    theme(
      panel.grid = element_blank(),
      axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
      axis.title = element_text(face = "bold")
    )

  dir.create(dirname(output_png), recursive = TRUE, showWarnings = FALSE)
  ggsave(output_png, plot = heatmap_plot, width = 11, height = 9, dpi=300, units = "in", scale=1)
}

plot_keyword_overlap_heatmap(
  keyword_overlap_spain_input,
  "./output/plots/keyword_overlap_sp.png",
  "Spain Keyword Overlap"
)

plot_keyword_overlap_heatmap(
  keyword_overlap_argentina_input,
  "./output/plots/keyword_overlap_arg.png",
  "Argentina Keyword Overlap"
)
